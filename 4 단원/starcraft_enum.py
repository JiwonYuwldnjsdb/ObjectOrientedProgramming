# 필요한 모듈 임포트
from dataclasses import dataclass
from abc import ABC, abstractmethod
import time
import threading
from enum import Enum, auto

def log_ability_usage(func):
    def wrapper(self, *args, **kwargs):
        print(f"{self.name}이(가) {func.__name__} 스킬 사용을 시도합니다.")
        return func(self, *args, **kwargs)
    return wrapper

# --- 게임 설정 상수 클래스 ---
class GameConfig:
    """게임의 모든 수치를 상수로 관리하여 유지보수성을 높입니다."""
    # 유닛 기본 능력치
    MARINE_HP = 40
    MARINE_POWER = 6
    ZERGLING_HP = 35
    ZERGLING_POWER = 5
    GHOST_HP = 45
    GHOST_POWER = 10

    # 유닛 특수 능력치
    ELITE_MARINE_ADVANTAGE = 10
    GHOST_MAX_ENERGY = 200
    GHOST_START_ENERGY = 75

    # 시나리오 전용 능력치
    SCENARIO_MARINE_HP = 50
    SCENARIO_GHOST_HP = 60

    # 능력치 회복 관련
    ZERGLING_HP_REGEN_RATE = 2
    GHOST_ENERGY_REGEN_RATE = 1

    # 스킬 관련
    CLOAK_COST = 25
    CLOAK_DURATION = 10
    LOCKDOWN_COST = 50
    LOCKDOWN_DURATION = 8


# --- 유닛 타입 열거형 ---
class UnitType(Enum):
    """생성 가능한 유닛의 종류를 정의하는 열거형"""
    MARINE = auto()
    ZERGLING = auto()
    GHOST = auto()

# --- Part 1: 모든 유닛의 청사진 ---
class Unit(ABC):
    """게임에 등장하는 단일 유닛을 나타내는 추상 기본 클래스입니다."""
    def __init__(self, name, hp, power):
        self.name = name
        self.max_hp = hp
        self._hp = hp
        self.power = power
        self.is_alive = True
        self.is_lockdown = False
    
    def __str__(self):
        return f"{self.name} (HP: {self._hp}/{self.max_hp})"

    def __repr__(self):
        return f"{self.__name__}(name='{self.name}', hp={self._hp}, power={self.power})"

    def move(self, x, y):
        """유닛을 새로운 위치로 이동시킵니다."""
        if not self.is_alive or self.is_lockdown:
            status = "파괴되어" if not self.is_alive else "락다운 상태라"
            print(f"{self.name}은(는) {status} 이동할 수 없습니다.")
            return
        print(f"{self.name}이(가) ({x}, {y}) 위치로 이동합니다.")

    @property
    def hp(self):
        return self._hp
    
    @hp.setter
    def hp(self, value):
        if value < 0:
            value = 0
        
        if value > self.max_hp:
            value = self.max_hp
        
        self._hp = value
    
    def take_damage(self, amount):
        """유닛의 HP를 주어진 양만큼 감소시킵니다."""
        if not self.is_alive: return
        self._hp = max(0, self._hp - amount)
        print(f"{self.name}이(가) {amount}의 데미지를 입었습니다. (남은 HP: {self._hp}/{self.max_hp})")
        if self._hp <= 0:
            self.is_alive = False
            print(f"*** {self.name}이(가) 파괴되었습니다. ***")

    def attack(self, target):
        """대상 유닛에 대한 공격을 시작합니다."""
        if not self.is_alive or self.is_lockdown:
            status = "파괴되어" if not self.is_alive else "락다운 상태라"
            print(f"{self.name}은(는) {status} 공격할 수 없습니다.")
            return

        if target.is_alive:
            self._do_attack(target)

    @abstractmethod
    def _do_attack(self, target):
        """실제 공격 로직을 수행합니다. 서브클래스에서 반드시 구현해야 합니다."""
        pass

    @staticmethod
    def calculate_hits_to_kill(hp, power):
        if power <= 0:
            return -1
        return hp // power

# --- 능력 믹스인(Mixin) 클래스 설계 ---
class CloakableMixin:
    """자동으로 해제되는 클로킹 능력을 제공하는 믹스인 클래스입니다."""
    @log_ability_usage
    def cloak(self, duration=GameConfig.CLOAK_DURATION):
        """유닛이 충분한 에너지를 가지고 있을 경우 클로킹을 활성화합니다."""
        if not self.is_alive: return
        cost = GameConfig.CLOAK_COST
        if hasattr(self, 'energy') and self.energy >= cost:
            self.energy -= cost
            self.is_cloaked = True
            print(f"{self.name}이(가) 클로킹을 사용합니다. ({duration}초 지속, 남은 에너지: {self.energy})")
            # 지속 시간이 지나면 클로킹 해제
            threading.Timer(duration, self.uncloak).start()
        else:
            print(f"{self.name}의 에너지가 부족하여 클로킹을 사용할 수 없습니다.")

    def uncloak(self):
        """클로킹 효과를 비활성화합니다."""
        if hasattr(self, 'is_cloaked') and self.is_cloaked:
            self.is_cloaked = False
            print(f">>> {self.name}의 클로킹 효과가 해제되었습니다. <<<")

class RegeneratableMixin:
    """매초 자동으로 HP를 회복하는 능력을 제공하는 믹스인 클래스입니다."""
    def _start_regeneration_process(self):
        """별도의 스레드에서 재생 루프를 시작합니다."""
        threading.Thread(target=self._regenerate_loop, daemon=True).start()

    def _regenerate_loop(self):
        """유닛이 살아있는 동안 지속적으로 HP를 재생합니다."""
        while self.is_alive:
            time.sleep(1)
            if self.is_alive and self.hp < self.max_hp:
                regen_rate = GameConfig.ZERGLING_HP_REGEN_RATE
                self.hp = min(self.max_hp, self.hp + regen_rate)
                print(f"[재생] {self.name}의 HP가 회복됩니다. (현재 HP: {self.hp}/{self.max_hp})")

class EnergyRegeneratableMixin:
    """매초 자동으로 에너지를 회복하는 능력을 제공하는 믹스인 클래스입니다."""
    def _start_energy_regeneration_process(self):
        """별도의 스레드에서 에너지 재생 루프를 시작합니다."""
        threading.Thread(target=self._energy_regenerate_loop, daemon=True).start()

    def _energy_regenerate_loop(self):
        """유닛이 살아있는 동안 지속적으로 에너지를 재생합니다."""
        while self.is_alive:
            time.sleep(1)
            if self.is_alive and hasattr(self, 'energy') and self.energy < self.max_energy:
                regen_rate = GameConfig.GHOST_ENERGY_REGEN_RATE
                self.energy = min(self.max_energy, self.energy + regen_rate)
                print(f"[에너지 회복] {self.name}의 에너지가 회복됩니다. (현재 에너지: {self.energy}/{self.max_energy})")


# --- 종족별 유닛 구현 ---
class Marine(Unit):
    """테란 마린 유닛을 나타냅니다."""
    def __init__(self, name="마린", hp=GameConfig.MARINE_HP, power=GameConfig.MARINE_POWER):
        super().__init__(name, hp, power)

    def _do_attack(self, target):
        print(f"{self.name}이(가) {target.name}을(를) 가우스 소총으로 공격!")
        target.take_damage(self.power)
        print(BattleLog(attacker_name=self.name, target_name=target.name, damage=self.power))
    
    @classmethod
    def create_elite_marine(self):
        return Marine(name="정예 마린", hp=GameConfig.MARINE_HP + GameConfig.ELITE_MARINE_ADVANTAGE, power=GameConfig.MARINE_POWER + GameConfig.ELITE_MARINE_ADVANTAGE)

class Zergling(Unit, RegeneratableMixin):
    """재생 능력을 가진 저그 저글링 유닛을 나타냅니다."""
    def __init__(self, name="저글링", hp=GameConfig.ZERGLING_HP, power=GameConfig.ZERGLING_POWER):
        super().__init__(name, hp, power)
        self._start_regeneration_process() # 생성 시 HP 회복 시작

    def _do_attack(self, target):
        print(f"{self.name}이(가) {target.name}을(를) 발톱으로 공격!")
        target.take_damage(self.power)
        print(BattleLog(attacker_name=self.name, target_name=target.name, damage=self.power))

class Ghost(Unit, CloakableMixin, EnergyRegeneratableMixin):
    """클로킹 및 락다운 능력을 가진 테란 고스트 유닛을 나타냅니다."""
    def __init__(self, name="고스트", hp=GameConfig.GHOST_HP, power=GameConfig.GHOST_POWER):
        super().__init__(name, hp, power)
        self.max_energy = GameConfig.GHOST_MAX_ENERGY
        self.energy = GameConfig.GHOST_START_ENERGY
        self.is_cloaked = False
        self._start_energy_regeneration_process() # 생성 시 에너지 회복 시작

    def _do_attack(self, target):
        print(f"{self.name}이(가) {target.name}을(를) C-10 저격소총으로 공격!")
        target.take_damage(self.power)
        print(BattleLog(attacker_name=self.name, target_name=target.name, damage=self.power))

    @log_ability_usage
    def lockdown(self, target, duration=GameConfig.LOCKDOWN_DURATION):
        """특정 시간 동안 대상 유닛을 비활성화시킵니다."""
        if not self.is_alive: return
        cost = GameConfig.LOCKDOWN_COST
        if self.energy >= cost:
            self.energy -= cost
            target.is_lockdown = True
            print(f"{self.name}이(가) {target.name}에게 락다운을 시전합니다! ({duration}초 지속)")

            def release_lockdown():
                if target.is_alive:
                    target.is_lockdown = False
                    print(f">>> {target.name}의 락다운 효과가 해제되었습니다. <<<")

            # 지속 시간이 지나면 락다운 해제
            threading.Timer(duration, release_lockdown).start()
        else:
            print(f"{self.name}의 에너지가 부족하여 락다운을 사용할 수 없습니다.")

# --- 유닛 생성 팩토리 클래스 ---
class UnitFactory:
    """다양한 종류의 유닛을 생성하기 위한 팩토리 클래스입니다."""
    def create_unit(self, unit_type: UnitType, name: str, **kwargs):
        """주어진 타입에 따라 유닛 인스턴스를 생성하고 반환합니다."""
        if unit_type == UnitType.MARINE:
            return Marine(name=name, **kwargs)
        elif unit_type == UnitType.ZERGLING:
            return Zergling(name=name, **kwargs)
        elif unit_type == UnitType.GHOST:
            return Ghost(name=name, **kwargs)
        else:
            raise ValueError(f"'{unit_type}'은(는) 생성할 수 없는 유닛 타입입니다.")

@dataclass(frozen=True)
class BattleLog:
    attacker_name: str
    target_name: str
    damage: int

# --- 게임 관리 클래스 ---
class GameManager:
    """전체 게임 상태, 유닛 생성, 시나리오를 관리합니다."""
    def __init__(self):
        self.units = []
        self.unit_factory = UnitFactory()

    def create_unit(self, unit_type: UnitType, name: str, *args, **kwargs):
        """팩토리를 사용하여 유닛을 생성하고 게임에 추가합니다."""
        try:
            unit = self.unit_factory.create_unit(unit_type, name, *args, **kwargs)
            if unit:
                self.units.append(unit)
                print(f"--- {name}({unit.__class__.__name__}) 생성 완료 ---")
            return unit
        except ValueError as e:
            print(e)
            return None

    def remove_dead_units(self):
        """파괴된 모든 유닛을 활성 유닛 목록에서 제거합니다."""
        self.units = [unit for unit in self.units if unit.is_alive]

    def run_scenario(self):
        """유닛 상호작용을 보여주기 위해 미리 정의된 게임 시나리오를 실행합니다."""
        # 1단계: 시나리오를 위한 유닛 생성 (사용자 지정 능력치 적용)
        marine = self.create_unit(UnitType.MARINE, "용감한 마린", hp=GameConfig.SCENARIO_MARINE_HP)
        marine = Marine.create_elite_marine()
        ghost = self.create_unit(UnitType.GHOST, "숙련된 고스트", hp=GameConfig.SCENARIO_GHOST_HP)
        zergling = self.create_unit(UnitType.ZERGLING, "날렵한 저글링")

        print("\n" + "="*30)
        print("### 시나리오 1: 고스트의 락다운과 에너지 회복 ###")
        print("="*30)

        # 2단계: 고스트가 마린에게 락다운 사용
        ghost.lockdown(marine, duration=4)
        time.sleep(1)

        # 3단계: 마린이 락다운 상태에서 공격 시도
        marine.attack(ghost)
        time.sleep(1)

        # 4단계: 고스트가 클로킹 사용
        ghost.cloak(duration=5)

        # 5단계: 락다운이 해제되기를 기다린 후, 마린이 다시 공격
        print("\n락다운이 해제되기를 기다립니다...")
        time.sleep(4)
        marine.attack(ghost)

        # 6단계: 고스트의 에너지가 회복되기를 기다린 후, 다시 락다운 사용
        print("\n고스트 에너지가 회복되기를 기다립니다 (5초)...")
        time.sleep(5)
        ghost.lockdown(marine, duration=2)

        print("\n" + "="*30)
        print("### 시나리오 2: 저글링의 전투와 자동 회복 ###")
        print("="*30)

        # 7단계: 마린과 저글링의 초기 교전
        marine.attack(zergling)
        zergling.attack(marine)

        # 8단계: 저글링의 자동 HP 회복을 보여주기 위해 대기
        print("\n저글링이 자동 회복하는 동안 대기합니다 (4초)...")
        time.sleep(4)

        # 9단계: 마린이 저글링이 파괴될 때까지 계속 공격
        while zergling.is_alive:
            if not marine.is_lockdown:
                marine.attack(zergling)
            time.sleep(0.5)

        # 10단계: 파괴된 유닛을 정리하고 최종 상태 보고
        self.remove_dead_units()
        print(f"\n시나리오 종료 후 생존 유닛: {[unit.name for unit in self.units]}")

# --- 시뮬레이션 실행 코드 ---
if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run_scenario()

