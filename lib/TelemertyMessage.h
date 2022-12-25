#ifndef STATEREPORTERLIB_TELEMERTYMESSAGE_H
#define STATEREPORTERLIB_TELEMERTYMESSAGE_H

#include <string>
#include <chrono>

namespace state_reporter {
    namespace details {

        struct TelemetryMessage {
            std::string module;
            std::string application;
            std::string param_name;
            std::string value;
            std::chrono::steady_clock::time_point timestamp;

            TelemetryMessage(const std::chrono::steady_clock::time_point timestamp, const std::string &module,
                             const std::string &application, const std::string &param_name, const std::string &value) :
                    module(module), application(application), param_name(param_name), value(value),
                    timestamp(timestamp) {}
        };

    } // namespace details
} // namespace state_reporter

#endif //STATEREPORTERLIB_TELEMERTYMESSAGE_H
