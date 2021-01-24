libAllPaths.so: main.o apmatrix.o Grammar.o Graph.o pathindex.o
	$(CXX) -shared $^ -o $@ -Wl,--whole-archive -lgraphblas -Wl,--no-whole-archive

main.o apmatrix.o Grammar.o Graph.o pathindex.o : CXXFLAGS+=-fPIC
