output: src/Math.cpp src/Trial.cpp
	g++ src/Trial.cpp -I /eigen-3.4.0/eigen/ -o build/output
	./build/output
clean:
	rm build/*