Interface.out: src/Interface.cpp src/Math.cpp
	g++ src/Interface.cpp -o Interface.out

run: Interface.out
	python3 src/Main.py

clean:
	rm Interface.out