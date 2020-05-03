from PRNG import PRNG

if __name__ == "__main__":
    print("HELLO")
    print(next(PRNG(['1111','1111','1111'], ['1111','1111','1111']).get_generator()))