# SPDX-License-Identifier: GPL-2.0-only
.SUFFIXES:
ifeq ($(strip $(DEVKITXENON)),)
$(error DEVKITXENON is not set. Use the free60/libxenon container)
endif

include $(DEVKITXENON)/rules

TARGET := xwtboot
BUILD := build
SOURCES := source
DATA :=
INCLUDES := source
CFLAGS := -O2 -Wall -Wextra $(MACHDEP) $(INCLUDE)
CXXFLAGS := $(CFLAGS)
LDFLAGS := $(MACHDEP) -Wl,--gc-sections -Wl,-Map,$(notdir $@).map
LIBS := -lxenon -lm -lfat
LIBDIRS :=

ifneq ($(BUILD),$(notdir $(CURDIR)))
export OUTPUT := $(CURDIR)/$(TARGET)
export VPATH := $(foreach dir,$(SOURCES),$(CURDIR)/$(dir))
export DEPSDIR := $(CURDIR)/$(BUILD)
CFILES := $(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.c)))
export LD := $(CC)
export OFILES := $(CFILES:.c=.o)
export INCLUDE := $(foreach dir,$(INCLUDES),-I$(CURDIR)/$(dir)) -I$(CURDIR)/$(BUILD) -I$(LIBXENON_INC)
export LIBPATHS := -L$(LIBXENON_LIB)
.PHONY: $(BUILD) clean all
all: $(BUILD)
$(BUILD):
	@mkdir -p $(BUILD)
	@$(MAKE) --no-print-directory -C $(BUILD) -f $(CURDIR)/Makefile
clean:
	@rm -rf $(BUILD) $(OUTPUT).elf $(OUTPUT).elf32
else
DEPENDS := $(OFILES:.o=.d)
$(OUTPUT).elf32: $(OUTPUT).elf
$(OUTPUT).elf: $(OFILES)
-include $(DEPENDS)
endif
