from abc import ABC, abstractmethod
import random

class EnergyPool:
    def __init__(self, current=0, maximum=200):
        self.current = current
        self.maximum = maximum
    
    def consume(self, amount):
        if amount <= 0:
            return True
        
        if self.current < amount:
            return False
        
        self.current -= amount
        
        return True
    
    def regen(self, amount):
        if amount <= 0:
            return 0
        
        before = self.current
        self.current = min(self.maximum, self.current + amount)
        
        return self.current - before

class CloakModule:
    def __init__(self, owner, energy_pool, activation_cost=25, drain_per_turn=10, duration=3):
        self.owner = owner
        self.energy_pool = energy_pool
        self.activation_cost = activation_cost
        self.drain_per_turn = drain_per_turn
        self.base_duration = duration
        self.is_cloaked = False
        self.remaining = 0

    def cloak(self):
        if hasattr(self.owner, "_islockdown") and not self.owner._islockdown():
            return
        
        if self.owner.hp == 0:
            return
        
        if self.is_cloaked:
            print(f"{self.owner.name}: 이미 은폐 상태입니다. ({self.remaining}턴 남음)")
            return
        
        if not self.energy_pool.consume(self.activation_cost):
            print(f"{self.owner.name}: 에너지가 부족하여 클로킹할 수 없습니다. ({self.energy_pool.current}/{self.activation_cost})")
            return
        
        self.is_cloaked = True
        self.remaining = self.base_duration
        print(f"{self.owner.name}: 클로킹 시작! (지속 {self.base_duration}턴, 활성화비 {self.activation_cost}, 매 턴 소모 {self.drain_per_turn})")

    def uncloak(self, reason="수동 해제"):
        if not self.is_cloaked:
            return
        
        self.is_cloaked = False
        self.remaining = 0
        print(f"{self.owner.name}: 클로킹 해제 ({reason}).")

    def update(self):
        if not self.is_cloaked:
            return
        
        if self.remaining > 0:
            self.remaining -= 1
        
        if not self.energy_pool.consume(self.drain_per_turn):
            self.uncloak("에너지 부족")
            return
        
        if self.remaining == 0:
            self.uncloak("지속시간 종료")

class RegenerationModule:
    def __init__(self, owner, amount=3):
        self.owner = owner
        self.amount = amount
    
    def regenerate(self):
        if self.owner.hp == 0:
            return
        
        before = self.owner.hp
        self.owner.hp = min(self.owner.max_hp, self.owner.hp + self.amount)
        healed = self.owner.hp - before
        
        if healed > 0:
            print(f"{self.owner.name}: 자가 회복 +{healed} (현재 HP {self.owner.hp}/{self.owner.max_hp})")

    def update(self):
        self.regenerate()

class BaseUnit(ABC):
    def __init__(self, hp=100, x=0, y=0, name="Default Unit", **kwargs):
        self.max_hp = hp
        self.hp = hp
        self.x = x
        self.y = y
        self.name = name
    
    def move(self, nx, ny):
        self.x, self.y = nx, ny
    
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

class GroundUnit(BaseUnit, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ground_unit = True

class AerialUnit(BaseUnit, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.air_unit = True

class MechanicUnit(BaseUnit, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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

class CreatureUnit(BaseUnit, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def update(self):
        pass

class Marine(GroundUnit, MechanicUnit):
    def __init__(self, hp=100, x=0, y=0, name="Default Marine"):
        super().__init__(hp=hp, x=x, y=y, name=name)
        self.gauss_dmg = 12
        
    def attack(self, other):
        if not self._islockdown():
            return
        
        if self.hp == 0:
            return
        
        other.attacked(self.gauss_dmg)
        print(f"{self.name}: 가우스 소총 발사! ({self.gauss_dmg} 피해)")
    
    def update(self):
        MechanicUnit.update(self)

class Zergling(GroundUnit, CreatureUnit):
    def __init__(self, hp=100, x=0, y=0, name="Default Zergling"):
        super().__init__(hp=hp, x=x, y=y, name=name)
        self.claw_dmg = 10
        
        self.regen = RegenerationModule(owner=self, amount=5)
    
    def attack(self, other):
        if self.hp == 0:
            return
        
        other.attacked(self.claw_dmg)
        print(f"{self.name}: 발톱으로 할퀴기! ({self.claw_dmg} 피해)")
    
    def regenerate(self):
        self.regen.regenerate()
    
    def update(self):
        self.regen.update()

class Zealot(GroundUnit, MechanicUnit):
    def __init__(self, hp=100, x=0, y=0, name="Default Zealot"):
        super().__init__(hp=hp, x=x, y=y, name=name)
        self.psionic_blade_dmg = 20
        
    def attack(self, other):
        if not self._islockdown():
            return
        
        if self.hp == 0:
            return
        
        other.attacked(self.psionic_blade_dmg)
        print(f"{self.name}: 사이오닉 검으로 공격! ({self.psionic_blade_dmg} 피해)")
    def update(self):
        
        MechanicUnit.update(self)

class Ghost(GroundUnit, MechanicUnit):
    DEFAULT_ENERGY = 50
    MAX_ENERGY = 200
    THRESHOLD = 100
    LOCKDOWN_TICKS = 3
    
    def __init__(self, hp=100, x=0, y=0, name="Default Ghost"):
        super().__init__(hp=hp, x=x, y=y, name=name)
        self.pistol_dmg = 8
        
        self.energy = EnergyPool(current=Ghost.DEFAULT_ENERGY, maximum=Ghost.MAX_ENERGY)
        self.cloaking = CloakModule(owner=self, energy_pool=self.energy,
                                    activation_cost=25, drain_per_turn=10, duration=3)
        
    def attack(self, other):
        if not self._islockdown():
            return
        
        if self.hp == 0:
            return
        
        other.attacked(self.pistol_dmg)
        print(f"{self.name}: 권총 사격! ({self.pistol_dmg} 피해)")
        
    def cloak(self):
        self.cloaking.cloak()
        
    def uncloak(self):
        self.cloaking.uncloak("수동 해제")
        
    def lockdown(self, other):
        if not self._islockdown():
            return
        
        if not isinstance(other, MechanicUnit):
            print(f"{self.name}: 대상이 기계 유닛이 아닙니다. 락다운 불가.")
            return
        
        if not self.energy.consume(Ghost.THRESHOLD):
            print(f"{self.name}: 에너지가 부족합니다. ({self.energy.current}/{Ghost.THRESHOLD})")
            return
        
        other.islockdown = True
        other.locktick = Ghost.LOCKDOWN_TICKS
        print(f"{self.name}: {other.name}에게 락다운 시전! ({Ghost.LOCKDOWN_TICKS}턴 지속)  남은 에너지 {self.energy.current}")
        
    def update(self):
        MechanicUnit.update(self)
        self.energy.regen(25)
        self.cloaking.update()

class Wraith(AerialUnit, MechanicUnit):
    DEFAULT_ENERGY = 60
    MAX_ENERGY = 200
    
    def __init__(self, hp=120, x=0, y=0, name="Default Wraith"):
        super().__init__(hp=hp, x=x, y=y, name=name)
        self.laser_dmg = 14
        
        self.energy = EnergyPool(current=Wraith.DEFAULT_ENERGY, maximum=Wraith.MAX_ENERGY)
        self.cloaking = CloakModule(owner=self, energy_pool=self.energy,
                                    activation_cost=25, drain_per_turn=12, duration=3)
    
    def attack(self, other):
        if not self._islockdown():
            return
        
        if self.hp == 0:
            return
        
        other.attacked(self.laser_dmg)
        print(f"{self.name}: 듀얼 레이저 발사! ({self.laser_dmg} 피해)")
        
    def cloak(self):
        self.cloaking.cloak()
        
    def uncloak(self):
        self.cloaking.uncloak("수동 해제")
        
    def update(self):
        MechanicUnit.update(self)
        self.energy.regen(20)
        self.cloaking.update()

if __name__ == "__main__":
    player1 = [Marine(100, 0, 0, "Marine1"),
               Marine(100, 1, 1, "Marine2"),
               Ghost(100, 2, 2, "Ghost1")]

    player2 = [Zergling(100, 0, 5, "Zergling1"),
               Zergling(100, 1, 6, "Zergling2"),
               Zergling(100, 2, 7, "Zergling3")]

    player3 = [Zealot(100, 0, 10, "Zealot1")]
    player4 = [Wraith(120, 5, 5, "Wraith1")]  # 신규 공중 유닛(클로킹 포함)

    players = [player1, player2, player3, player4]

    print("\n=== Turn 1: 교전 시작 ===")
    player1[0].attack(player2[0])   # Marine1 -> Zergling1
    player2[0].attack(player1[0])   # Zergling1 -> Marine1
    player1[1].attack(player2[1])   # Marine2 -> Zergling2
    player2[1].attack(player1[1])   # Zergling2 -> Marine2
    player3[0].attack(player1[0])   # Zealot1 -> Marine1

    # 락다운(에너지 100 필요, 고스트 기본 50이므로 실패 메시지 확인용)
    player1[2].lockdown(player3[0])

    # 클로킹 시연 (고스트/레이스)
    player1[2].cloak()
    player4[0].cloak()

    # 저글링 자가 회복 시연: 먼저 피해를 입힌 후 regenerate() 직접 호출
    player2[0].attacked(30)
    player2[0].regenerate()  # 명시적 회복

    # 1턴 업데이트(락다운 카운트, 에너지 회복, 클로킹 지속/소모, 저그 자동 회복)
    for team in players:
        for unit in team:
            unit.update()

    # 몇 턴 더 진행하여 클로킹 자동 해제/저그 자동 회복을 확인
    for t in range(2, 6):
        print(f"\n=== Turn {t} ===")
        player3[0].attack(player1[0])
        player1[0].attack(player2[random.randrange(0, len(player2))])
        player2[2].attack(player1[random.randrange(0, len(player1))])
        player1[2].attack(player2[random.randrange(0, len(player2))])
        player4[0].attack(player2[0])
        for team in players:
            for unit in team:
                unit.update()
