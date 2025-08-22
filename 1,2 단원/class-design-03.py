class CharacterStats:
    MAX_LEVEL = 100
    
    def __init__(self, hp, mp, strength, dexterity, intelligence):
        self.hp = hp
        self.mp = mp
        self.strength = strength
        self.dexterity = dexterity
        self.intelligence = intelligence
    
    def is_alive(self):
        if self.hp > 0:
            return True
        else:
            return False
    
    def boost_stat(self, stat_name, value):
        eval(f"self.{stat_name} += {value}")
    
    def get_info(self):
        print('-' * 10, '캐리터 정보', '-' * 10)
        print(f"캐릭터의 체력:\t{self.hp:>5}")
        print(f"캐릭터의 마나:\t{self.mp:>5}")
        print(f"캐릭터의 힘:\t{self.strength:>5}")
        print(f"캐릭터의 민첩:\t{self.dexterity:>5}")
        print(f"캐릭터의 지능:\t{self.intelligence:>5}")

player1 = CharacterStats(120, 50, 5, 10, 70)
player2 = CharacterStats(200, 5, 60, 20, 10)
player3 = CharacterStats(150, 20, 40, 70, 30)

player1.get_info()
player2.get_info()
player3.get_info()