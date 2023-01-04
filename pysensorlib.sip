%Module(name=sensorlib, language="C")
const char *StateReporter_init(const char *module, const char *app);
void StateReporter_stop();
void StateReporter_set_value(const char *value, const char *function, const char *description);

