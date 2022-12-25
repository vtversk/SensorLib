#include "StateReporter.h"
#include "StateReporterC.h"

extern "C"
{
const char *StateReporter_init(const char *module, const char *app) {
    try {
        state_reporter::StateReporter::getInstance().init(std::string(ip), port, std::string(module), std::string(app));
    } catch (const std::exception &ex) {
        return ex.what();
    }
    return nullptr;
}

void StateReporter_stop() {
    state_reporter::StateReporter::getInstance().stop();
}

void StateReporter_set_value(const char *value, const char *function, const char *description) {
	double val = atof(value);
	ApplicationState state = APPLICATION_STATE_UNKNOWN;
	if (val > -2 && val < 4){
		state = APPLICATION_STATE_NORMAL;
	}
	else if (val >= 4 && val < 7){
		state = APPLICATION_STATE_ERROR;
	}
	else if (val >= 7 && val < 10){
		state = APPLICATION_STATE_WARNING;
	}
    state_reporter::StateReporter::getInstance().set_permanent_state(std::string(function), state, std::string(description));
}

}
