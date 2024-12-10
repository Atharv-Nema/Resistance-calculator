build/Interface.out: src/Interface.cpp src/Math.cpp
	g++ src/Interface.cpp -o build/Interface.out

run: build/Interface.out
	python3 src/Main.py

clean:
	rm -rf build