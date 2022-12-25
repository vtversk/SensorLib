#ifndef STATEREPORTERLIBC_LIBRARY_H
#define STATEREPORTERLIBC_LIBRARY_H

#include "State.h"

#ifdef __cplusplus
extern "C"
{
#endif
const char *StateReporter_init(const char *module, const char *app);
void StateReporter_stop();

void StateReporter_set_value(const char *value, const char *function, const char *description);

const char *ip = "127.0.0.1";
int port = 3333;
const char *module = "System15CriticalMonitor_#23";
const char *app = "EnergyTanker11P340T";

#ifdef __cplusplus
}
#endif
#endif
