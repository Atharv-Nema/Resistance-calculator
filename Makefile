CC = g++
CFLAGS = -I /eigen-3.4.0/eigen/
SRC_DIR = src
BUILD_DIR = build

all: $(BUILD_DIR)/Trial

$(BUILD_DIR)/Trial: $(SRC_DIR)/Trial.cpp
	$(CC) $(CFLAGS) $^ -o $@

run: $(BUILD_DIR)/Trial
	./$(BUILD_DIR)/Trial

clean:
	rm -rf $(BUILD_DIR)/Trial