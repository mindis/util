CXX = g++

LDFLAGS = -lpthread -fopenmp
CFLAGS = -O3 -Wall -Iinclude -std=c++0x -fopenmp

CFLAGS += -Iinclude/include

DIR_SRC = ./src

SRC = $(wildcard $(DIR_SRC)/*.cc)

OBJ = $(patsubst %.cc,$(DIR_SRC)/%.o,$(notdir $(SRC)))
OBJ += ./lib/libdmlc.a

target = ./bin/lbfgs

$(target) : $(OBJ)
	$(CXX) $(OBJ) -o $@ $(LDFLAGS)

$(DIR_SRC)/%.o : $(DIR_SRC)/%.cc
	$(CXX) $(CFLAGS) -c $< -o $@

.PHONY:clean

clean:
	$(RM) $(DIR_SRC)/*.o
	$(RM) ./bin/lbfgs
