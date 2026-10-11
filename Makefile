BUILD_DIR ?= build
OUTPUT    := $(BUILD_DIR)/libcursortrail.so

.PHONY: all clean load unload reload

all:
	cmake -S . -B $(BUILD_DIR) -DCMAKE_BUILD_TYPE=Release
	cmake --build $(BUILD_DIR) -j$$(nproc)

clean:
	rm -rf $(BUILD_DIR)

# handy while developing: hot-(re)load into the running Hyprland
load: all
	hyprctl plugin load $(CURDIR)/$(OUTPUT)

unload:
	hyprctl plugin unload $(CURDIR)/$(OUTPUT)

reload: unload load
