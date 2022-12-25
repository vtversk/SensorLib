#include "StateReporter.h"

#include <unistd.h>
#include <iostream>
#include <string.h>

namespace {
#pragma pack(push, 1)
    struct StateReporterAgentProtocolHdr {
        uint8_t magic; // should be 0xFF
        uint8_t message_type;
        uint16_t payload_length;
    };
#pragma pack(pop)

    typedef enum {
        MESSAGE_TYPE_STATE = 1,
        MESSAGE_TYPE_TELEMETRY = 2
    } StateReporterMessageType;


    class StateReportMessageComposer {
        using chunk = std::vector<char>;
        static constexpr size_t MAX_MESSAGE_SIZE = 65530;
    public:

        explicit StateReportMessageComposer(std::queue<state_reporter::StateReporter::OutgoingBuffer> &storage)
                : storage(storage) {
            prepare_new_chunk();
        }

        ~StateReportMessageComposer() {}

        void finish_current_chunk() {
            storage.emplace();
            storage.back().second = last_timestamp;
            std::swap(storage.back().first, current_chunk);
        }

        void push_message(const std::string &message, std::chrono::steady_clock::time_point message_timestamp,
                          StateReporterMessageType message_type = MESSAGE_TYPE_STATE) {
            if (message.length() > MAX_MESSAGE_SIZE) {
                // should we ignore this super long message?
                return;
            }
            prepare_current_chunk(message.length() + sizeof(StateReporterAgentProtocolHdr));
            push_header(message.length(), message_type);
            std::copy(message.begin(), message.end(), std::back_inserter(current_chunk));
            last_timestamp = message_timestamp;
        }

    private:
        void prepare_new_chunk() {
            current_chunk.reserve(MAX_MESSAGE_SIZE);
        }

        void prepare_current_chunk(size_t requested_free_bytes) {
            if ((current_chunk.size() + requested_free_bytes) >= MAX_MESSAGE_SIZE) {
                finish_current_chunk();
                prepare_new_chunk();
            }
        }

        void push_header(size_t payload, StateReporterMessageType message_type) {
            StateReporterAgentProtocolHdr hdr;
            hdr.magic = 0xFF;
            hdr.message_type = static_cast<uint8_t>(message_type);
            hdr.payload_length = static_cast<uint16_t>(payload);
            auto pos = current_chunk.size();
            current_chunk.resize(pos + 4);
            memcpy(current_chunk.data() + pos, &hdr, sizeof(hdr));
        }

        chunk current_chunk;
        std::chrono::steady_clock::time_point last_timestamp;
        std::queue<state_reporter::StateReporter::OutgoingBuffer> &storage;
    };

}

void state_reporter::StateReporter::init(const std::string &ip, int16_t port, const std::string &module,
                                         const std::string &app) {
    this->module_def = module;
    this->application_def = app;
    this->ip = ip;
    this->port = port;

    auto time_now = std::chrono::steady_clock::now();

    StateMessage msg(time_now, ApplicationState::APPLICATION_STATE_NORMAL, module_def, application_def, "", "");
    ok_msg = state_message_to_json(msg);

    thread = std::thread([&]() {
        sender();
    });
}

void
state_reporter::StateReporter::send_exception(const std::string &function, ApplicationState state,
                                              const std::string &description) {
    send_exception(module_def, application_def, function, state, description);
}

void
state_reporter::StateReporter::send_exception(const std::string &module, const std::string &application,
                                              const std::string &function, ApplicationState state,
                                              const std::string &description) {
    auto time_now = std::chrono::steady_clock::now();

    std::lock_guard<std::mutex> locker(queue_locker);
    StateMessage msg(time_now, state, module, application, function, description);
    msgs.push(msg);

    // remove old messages
    auto min_timestamp_for_send = time_now - TIMEOUT * 300;
    while (!msgs.empty() && (msgs.front().timestamp < min_timestamp_for_send)) {
        msgs.pop();
    }
}

void state_reporter::StateReporter::set_permanent_state(const std::string &function, ApplicationState state,
                                                        const std::string &description) {
    set_permanent_state(module_def, application_def, function, state, description);
}

void state_reporter::StateReporter::set_permanent_state(const std::string &module, const std::string &application,
                                                        const std::string &function, ApplicationState state,
                                                        const std::string &description) {
    auto time_now = std::chrono::steady_clock::now();

    std::lock_guard<std::mutex> locker(queue_locker);
    std::string fullname = module + "." + application + "." + function;
    auto it = permanent_msgs.find(fullname);
    if (it != permanent_msgs.end()) {
        it->second.state = state;
        it->second.description = description;
        it->second.timestamp = time_now;
    } else {
        permanent_msgs[fullname] = StateMessage(time_now, state, module, application, function, description);
    }
}

void state_reporter::StateReporter::send_telemetry(const std::string &telemetry_param, const std::string &value) {
    send_telemetry(module_def, application_def, telemetry_param, value);
}

void state_reporter::StateReporter::send_telemetry(const std::string &module, const std::string &application,
                                                   const std::string &telemetry_param, const std::string &value) {
    auto time_now = std::chrono::steady_clock::now();

    std::lock_guard<std::mutex> locker(queue_locker);
    details::TelemetryMessage msg(time_now, module, application, telemetry_param, value);
    telemetry_msgs.push(msg);

    // remove old messages
    auto min_timestamp_for_send = time_now - TIMEOUT * 300;
    while (!telemetry_msgs.empty() && (telemetry_msgs.front().timestamp < min_timestamp_for_send)) {
        telemetry_msgs.pop();
    }
}

void state_reporter::StateReporter::reset_permanent_state(const std::string &function) {
    reset_permanent_state(module_def, application_def, function);
}

void state_reporter::StateReporter::reset_permanent_state(const std::string &module, const std::string &application,
                                                          const std::string &function) {
    std::lock_guard<std::mutex> locker(queue_locker);
    std::string fullname = module + "." + application + "." + function;
    auto it = permanent_msgs.find(fullname);
    if (it != permanent_msgs.end()) {
        msgs.push(it->second);
        permanent_msgs.erase(it);
    }
}

void state_reporter::StateReporter::sender() {
    is_running = true;
    while (is_running) {
        if (!is_connected()) {
            try_to_connect();
        }

        if (is_connected()) {
            prepare_messages();
            send_prepared_messages();
        }

        std::this_thread::sleep_for(TIMEOUT);
    }
    if (is_connected()) {
        close(client_sock);
    }
}

std::string state_reporter::StateReporter::state_message_to_json(const StateMessage &msg) {
    return R"({"state":")" + std::to_string(msg.state) + R"(","module":")" + msg.module + R"(", "app":")" +
           msg.application +
           R"(","func":")" + msg.function + R"(","desc":")" + msg.description + "\"}";
}

std::string state_reporter::StateReporter::telemetry_message_to_json(const details::TelemetryMessage &msg) {
    return R"({"value":")" + msg.value + R"(","module":")" + msg.module + R"(", "app":")" + msg.application +
           R"(","param":")" + msg.param_name + "\"}";
}

void state_reporter::StateReporter::try_to_connect() {
    sockaddr_in addr;
    memset(&addr, 0, sizeof(struct sockaddr_in));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(static_cast<uint16_t>(port));
    addr.sin_addr.s_addr = inet_addr(ip.c_str());

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        return;
    }

    int len = BUFFER_SIZE;
    #ifdef WIN32
    int rc = setsockopt(sock, SOL_SOCKET, SO_SNDBUF, (const char *) &len, sizeof(len));
    #else
    int rc = setsockopt(sock, SOL_SOCKET, SO_SNDBUF, (const void *) &len, sizeof(len));
    #endif
    if (rc < 0) {
        close(sock);
        return;
    }
    #ifdef WIN32
    rc = setsockopt(sock, SOL_SOCKET, SO_RCVBUF, (const char *) &len, sizeof(len));
    #else
    rc = setsockopt(sock, SOL_SOCKET, SO_RCVBUF, (const char *) &len, sizeof(len));
    #endif
    if (rc < 0) {
        close(sock);
        return;
    }
    rc = ::connect(sock, (struct sockaddr *) &addr, sizeof(struct sockaddr_in));
    if (rc < 0) {
        close(sock);
        return;
    }

    client_sock = sock;
}

bool state_reporter::StateReporter::is_connected() {
    return (client_sock != -1);
}

void state_reporter::StateReporter::prepare_messages() {
    StateReportMessageComposer composer(outgoing_queue);
    std::lock_guard<std::mutex> lock_guard(queue_locker);

    if (msgs.empty() && permanent_msgs.empty()) {
        //must send ok state
        composer.push_message(ok_msg, std::chrono::steady_clock::now());
    } else {
        while (!msgs.empty()) {
            auto msg = msgs.front();
            msgs.pop();
            composer.push_message(state_message_to_json(msg), msg.timestamp);
        }
        for (auto &msg : permanent_msgs) {
            composer.push_message(state_message_to_json(msg.second), std::chrono::steady_clock::now());
        }
    }
    while (!telemetry_msgs.empty()) {
        auto msg = telemetry_msgs.front();
        telemetry_msgs.pop();
        composer.push_message(telemetry_message_to_json(msg), msg.timestamp, MESSAGE_TYPE_TELEMETRY);
    }
    composer.finish_current_chunk();
}

void state_reporter::StateReporter::send_prepared_messages() {
    while (!outgoing_queue.empty()) {
        // check for old composed messages
        auto min_timestamp_for_send = std::chrono::steady_clock::now() - TIMEOUT * 300;
        if (outgoing_queue.front().second < min_timestamp_for_send) {
            outgoing_queue.pop();
            continue;
        }

        std::vector<char> &current_piece = outgoing_queue.front().first;
        size_t already_sent = 0;

        while (already_sent != current_piece.size()) {
            int flag = 0;
            #ifndef WIN32
            flag = MSG_NOSIGNAL;
            #endif
            size_t rc = send(client_sock, current_piece.data() + already_sent, current_piece.size() - already_sent,
                              flag);
            
            if (rc < 0) {
                if (errno != EWOULDBLOCK && errno != EAGAIN && errno != EINTR) {
                    // some error on socket
                    close(client_sock);
                    client_sock = -1;
                    return;
                }
            } else {
                already_sent += rc;
            }
        }
        outgoing_queue.pop();
    }
}
