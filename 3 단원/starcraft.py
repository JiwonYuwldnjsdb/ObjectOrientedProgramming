from abc import ABC, abstractmethod
import random

class Unit(ABC):
    def __init__(self, hp=100, x=0, y=0, name="Default Unit"):
        self.hp = hp
        self.x = x
        self.y = y
        self.name = name

    def move(self, nx, ny):
        self.x = nx
        self.y = ny
    
    def attacked(self, dmg):
        if self.hp == 0:
            return
        self.hp = max(self.hp - dmg, 0)
        if self.hp == 0:
            print(f"Unit {self.name}이(가) 사망하였습니다.")

    @abstractmethod
    def attack(self, other):
        pass

    @abstractmethod
    def update(self):
        pass

class MechanicUnit(Unit, ABC):
    def __init__(self, hp=100, x=0, y=0, name="Mechanic Unit"):
        super().__init__(hp, x, y, name)
        self.islockdown = False
        self.locktick = 0

    def _islockdown(self):
        if self.islockdown:
            print(f"{self.name}은(는) 락다운 상태라 행동할 수 없습니다. ({self.locktick}턴 남음)")
            return False
        return True

    def update(self):
        if self.locktick > 0:
            self.locktick -= 1
            if self.locktick == 0:
                self.islockdown = False
                print(f"{self.name}의 락다운이 해제되었습니다.")

class CreatureUnit(Unit, ABC):
    def __init__(self, hp=100, x=0, y=0, name="Creature Unit"):
        super().__init__(hp, x, y, name)

    def update(self):
        pass

class Marine(MechanicUnit):
    def __init__(self, hp=100, x=0, y=0, name="Default Marine"):
        super().__init__(hp, x, y, name)
        self.gauss_dmg = 12

    def attack(self, other):
        if not self._islockdown():
            return
        if self.hp == 0:
            return
        other.attacked(self.gauss_dmg)
        print(f"{self.name}: 가우스 소총 발사! ({self.gauss_dmg} 피해)")


class Zergling(CreatureUnit):
    def __init__(self, hp=100, x=0, y=0, name="Default Zergling"):
        super().__init__(hp, x, y, name)
        self.claw_dmg = 10

    def attack(self, other):
        if self.hp == 0:
            return
        other.attacked(self.claw_dmg)
        print(f"{self.name}: 발톱으로 할퀴기! ({self.claw_dmg} 피해)")

class Zealot(MechanicUnit):
    def __init__(self, hp=100, x=0, y=0, name="Default Zealot"):
        super().__init__(hp, x, y, name)
        self.psionic_blade_dmg = 20

    def attack(self, other):
        if not self._islockdown():
            return
        if self.hp == 0:
            return
        other.attacked(self.psionic_blade_dmg)
        print(f"{self.name}: 사이오닉 검으로 공격! ({self.psionic_blade_dmg} 피해)")

class Ghost(MechanicUnit):
    DEFAULT_ENERGY = 50
    MAX_ENERGY = 200
    THRESHOLD = 100
    LOCKDOWN_TICKS = 3

    def __init__(self, hp=100, x=0, y=0, name="Default Ghost"):
        super().__init__(hp, x, y, name)
        self.energy = Ghost.DEFAULT_ENERGY
        self.pistol_dmg = 8

    def attack(self, other):
        if not self._islockdown():
            return
        if self.hp == 0:
            return
        other.attacked(self.pistol_dmg)
        print(f"{self.name}: 권총 사격! ({self.pistol_dmg} 피해)")

    def lockdown(self, other):
        if not self._islockdown():
            return
        if not isinstance(other, MechanicUnit):
            print(f"{self.name}: 대상이 기계 유닛이 아닙니다. 락다운 불가.")
            return
        if self.energy < Ghost.THRESHOLD:
            print(f"{self.name}: 에너지가 부족합니다. ({self.energy}/{Ghost.THRESHOLD})")
            return
        self.energy -= Ghost.THRESHOLD
        other.islockdown = True
        other.locktick = Ghost.LOCKDOWN_TICKS
        print(f"{self.name}: {other.name}에게 락다운 시전! ({Ghost.LOCKDOWN_TICKS}턴 지속)  남은 에너지 {self.energy}")

    def update(self):
        super().update()
        before = self.energy
        self.energy = min(self.energy + 25, Ghost.MAX_ENERGY)
        if self.energy != before:
            pass

player1 = [Marine(100, 0, 0, "Marine1"),
           Marine(100, 1, 1, "Marine2"),
           Ghost(100, 2, 2, "Ghost1")]

player2 = [Zergling(100, 0, 5, "Zergling1"),
           Zergling(100, 1, 6, "Zergling2"),
           Zergling(100, 2, 7, "Zergling3")]

player3 = [Zealot(100, 0, 10, "Zealot1")]

players = [player1, player2, player3]

print("\n=== Turn 1: 교전 시작 ===")
player1[0].attack(player2[0])   # Marine1 -> Zergling1
player2[0].attack(player1[0])   # Zergling1 -> Marine1
player1[1].attack(player2[1])   # Marine2 -> Zergling2
player2[1].attack(player1[1])   # Zergling2 -> Marine2
player3[0].attack(player1[0])   # Zealot1 -> Marine1
player1[2].lockdown(player3[0]) # Ghost1 -> Zealot1 락다운

for team in players:
    for unit in team:
        unit.update()

for t in range(2, 21):
    print(f"\n=== Turn {t} ===")
    player3[0].attack(player1[random.randrange(0, len(player1) - 1)])
    player1[0].attack(player2[random.randrange(0, len(player2) - 1)])
    player2[2].attack(player1[random.randrange(0, len(player1) - 1)])
    player1[2].attack(player2[random.randrange(0, len(player2) - 1)])
    for team in players:
        for unit in team:
            unit.update()

"""
각 유닛은 자신의 클래스(Marine, Zergling, Zealot, Ghost)에서 attack() 메서드를
오버라이드(override)했기 때문에 고유한 공격 메시지를 출력할 수 있다.

이것이 가능한 이유는 다형성(polymorphism) 때문이다.
부모 클래스(Unit)의 추상 메서드 attack()을 상속받은 자식 클래스들이
각자의 방식대로 구현(override)하면,
동일한 unit.attack(target) 호출이라도 실제로는
그 객체의 실제 타입에 맞는 메서드가 실행된다.

즉, Marine은 "가우스 소총 발사!", Zergling은 "발톱으로 할퀴기!",
Zealot은 "사이오닉 검으로 공격!", Ghost는 "권총 사격!" 이라는
메시지를 개별적으로 출력할 수 있다.
"""
