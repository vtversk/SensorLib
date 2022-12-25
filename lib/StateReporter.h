#ifndef STATEREPORTERLIB_LIBRARY_H
#define STATEREPORTERLIB_LIBRARY_H

#include <string>
#ifdef __WIN32
#include <winsock.h>
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#endif

#include <queue>
#include <mutex>
#include <atomic>
#include <memory>
#include <thread>
#include <map>
#include <chrono>


#include "State.h"
#include "StateMessage.h"
#include "TelemertyMessage.h"

using namespace std::chrono_literals;

namespace state_reporter {
    class StateReporter {
        const int BUFFER_SIZE = 1024;
        const std::chrono::milliseconds TIMEOUT = 900ms;
    public:
        using OutgoingBuffer = std::pair<std::vector<char>, std::chrono::steady_clock::time_point>;
    public:
        void init(const std::string &ip, int16_t port, const std::string &module, const std::string &app);

        void send_exception(const std::string &function, ApplicationState state, const std::string &description);

        void send_exception(const std::string &module, const std::string &application, const std::string &function,
                            ApplicationState state, const std::string &description);

        void send_telemetry(const std::string &telemetry_param, const std::string &value);

        void send_telemetry(const std::string &module, const std::string &application, const std::string &telemetry_param, const std::string &value);

        void set_permanent_state(const std::string &function, ApplicationState state, const std::string &description);

        void set_permanent_state(const std::string &module, const std::string &application, const std::string &function,
                                 ApplicationState state, const std::string &description);

        void reset_permanent_state(const std::string &function);

        void
        reset_permanent_state(const std::string &module, const std::string &application, const std::string &function);

        void stop() {
            is_running = false;
            if (thread.joinable()) {
                thread.join();
            }
        }

        static StateReporter &getInstance() {
            static StateReporter instance;
            return instance;
        }

    private:
        std::string ip;
        int16_t port = 0;

        int client_sock = -1;
        std::string module_def;
        std::string application_def;
        std::queue<StateMessage> msgs;
        std::queue<details::TelemetryMessage> telemetry_msgs;
        std::map<std::string, StateMessage> permanent_msgs;
        std::mutex queue_locker;

        std::atomic<bool> is_running{};
        std::thread thread;

        std::string ok_msg;

        StateReporter() { is_running = false; }

        StateReporter(const StateReporter &) = delete;

        StateReporter &operator=(StateReporter &) = delete;

        ~StateReporter() {
            stop();
        }

        void sender();

        void try_to_connect();

        bool is_connected();

        void prepare_messages();

        void send_prepared_messages();

        std::string state_message_to_json(const StateMessage &msg);

        std::string telemetry_message_to_json(const details::TelemetryMessage &msg);

        std::queue<OutgoingBuffer> outgoing_queue;
    };
}
#endif