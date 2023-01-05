cd lib
cmake .
make
cp libStateReporterLib.a libStateReporterLib.lib
cd ..
sip-build --verbose
sip-install
