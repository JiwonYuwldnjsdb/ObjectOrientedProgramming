# 필요한 모듈 임포트
from abc import ABC, abstractmethod
import time
import threading
from enum import Enum, auto
from dataclasses import dataclass

# --- 미션 5: 전투 기록 표준화 (@dataclass 활용) ---
@dataclass(frozen=True)
class BattleLog:
    """전투 기록을 담는 불변 데이터 클래스"""
    attacker_name: str
    target_name: str
    damage: int

# --- 미션 4: 특수 능력 사용 기록기 개발 (커스텀 데코레이터 활용) ---
def log_ability_usage(func):
    """스킬 사용 시 로그를 출력하는 데코레이터"""
    def wrapper(self, *args, **kwargs):
        print(f"-> {self.name}이(가) '{func.__name__}' 스킬 사용을 시도합니다.")
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

    # 시나리오 전용 정예 유닛 능력치
    SCENARIO_MARINE_HP = 50
    SCENARIO_GHOST_HP = 60
    ELITE_MARINE_HP_BONUS = 10
    ELITE_MARINE_POWER_BONUS = 10

    # 유닛 특수 능력치
    GHOST_MAX_ENERGY = 200
    GHOST_START_ENERGY = 75

    # 능력치 회복 관련
    ZERGLING_HP_REGEN_RATE = 2
    GHOST_ENERGY_REGEN_RATE = 1

    # 스킬 관련
    CLOAK_COST = 25
    CLOAK_DURATION = 10
    LOCKDOWN_COST = 50
    LOCKDOWN_DURATION = 8

    # --- (전략 패턴) 스팀팩 관련 ---
    STIMPACK_HP_COST = 5
    STIMPACK_POWER_BONUS = 6  # 예: 기본 공격력에 +6

# --- 유닛 타입 열거형 ---
class UnitType(Enum):
    MARINE = auto()
    ZERGLING = auto()
    GHOST = auto()

# --------------------------------------------------------------------
# 미션 1: 역할 분담과 의존성 역전 (SRP, DIP 적용)
# --------------------------------------------------------------------
class BattleReporter(ABC):
    """출력 매체에 독립적인 전투/시나리오 보고 추상화"""
    @abstractmethod
    def log(self, message: str) -> None:
        pass

class ConsoleReporter(BattleReporter):
    """콘솔에 출력하는 구체 구현"""
    def log(self, message: str) -> None:
        print(message)

# --------------------------------------------------------------------
# 미션 2: 전투 방식의 교체 (전략 패턴)
# --------------------------------------------------------------------
class AttackStrategy(ABC):
    """공격 알고리즘 추상화"""
    @abstractmethod
    def execute(self, attacker, target) -> None:
        """attacker가 target을 공격한다."""
        pass

class GaussRifleStrategy(AttackStrategy):
    """마린: 가우스 소총"""
    def execute(self, attacker, target) -> None:
        if not attacker.is_alive or attacker.is_lockdown: return
        damage = attacker.power
        print(f"{attacker.name} -> {target.name} (가우스 소총 공격!)")
        print(BattleLog(attacker.name, target.name, damage))
        target.take_damage(damage)

class ClawStrategy(AttackStrategy):
    """저글링: 발톱 공격"""
    def execute(self, attacker, target) -> None:
        if not attacker.is_alive or attacker.is_lockdown: return
        damage = attacker.power
        print(f"{attacker.name} -> {target.name} (발톱 공격!)")
        print(BattleLog(attacker.name, target.name, damage))
        target.take_damage(damage)

class SniperRifleStrategy(AttackStrategy):
    """고스트: C-10 저격소총"""
    def execute(self, attacker, target) -> None:
        if not attacker.is_alive or attacker.is_lockdown: return
        damage = attacker.power
        print(f"{attacker.name} -> {target.name} (C-10 저격소총 공격!)")
        print(BattleLog(attacker.name, target.name, damage))
        target.take_damage(damage)

class StimpackStrategy(AttackStrategy):
    """(도전) 마린: 스팀팩—HP를 소모하고 더 강하게 공격"""
    def execute(self, attacker, target) -> None:
        if not attacker.is_alive or attacker.is_lockdown: return
        hp_cost = GameConfig.STIMPACK_HP_COST
        print(f"{attacker.name}이(가) 스팀팩을 사용합니다! (HP -{hp_cost}, 공격력 +{GameConfig.STIMPACK_POWER_BONUS})")
        attacker.take_damage(hp_cost)
        if not attacker.is_alive:  # 스팀팩 과다 사용으로 사망할 수 있음
            return
        damage = attacker.power + GameConfig.STIMPACK_POWER_BONUS
        print(f"{attacker.name} -> {target.name} (스팀팩 가우스 소총 연사!)")
        print(BattleLog(attacker.name, target.name, damage))
        target.take_damage(damage)

# --------------------------------------------------------------------
# 미션 3: 유닛 강화 시스템 (데코레이터 패턴)
# --------------------------------------------------------------------
class UnitDecorator(ABC):
    """Unit과 동일 인터페이스를 따르며, 다른 Unit을 감싼다."""
    def __init__(self, unit):
        self.wrapped_unit = unit

    # 기본 위임: 존재하지 않는 속성/메서드는 원본 유닛에 위임
    def __getattr__(self, attr):
        return getattr(self.wrapped_unit, attr)

    # 주요 속성/메서드 노출 및 위임
    @property
    def name(self):
        return self.wrapped_unit.name

    @property
    def max_hp(self):
        return self.wrapped_unit.max_hp

    @property
    def hp(self):
        return self.wrapped_unit.hp

    @hp.setter
    def hp(self, v):
        self.wrapped_unit.hp = v

    @property
    def is_alive(self):
        return self.wrapped_unit.is_alive

    @is_alive.setter
    def is_alive(self, v):
        self.wrapped_unit.is_alive = v

    @property
    def is_lockdown(self):
        return self.wrapped_unit.is_lockdown

    @is_lockdown.setter
    def is_lockdown(self, v):
        self.wrapped_unit.is_lockdown = v

    @property
    def attack_strategy(self):
        return self.wrapped_unit.attack_strategy

    @attack_strategy.setter
    def attack_strategy(self, s):
        self.wrapped_unit.attack_strategy = s

    @property
    def power(self):
        # 기본은 원본 power 그대로
        return self.wrapped_unit.power

    def set_strategy(self, new_strategy):
        self.wrapped_unit.set_strategy(new_strategy)

    def move(self, x, y):
        self.wrapped_unit.move(x, y)

    def take_damage(self, amount):
        self.wrapped_unit.take_damage(amount)

    def attack(self, target):
        self.wrapped_unit.attack(target)

    def __str__(self):
        return f"{self.wrapped_unit} [+UPG]"

    def __repr__(self):
        return f"UnitDecorator({repr(self.wrapped_unit)})"

class DamageUpgradeDecorator(UnitDecorator):
    """무기 업그레이드(+보너스) 적용 데코레이터: power만 증강"""
    def __init__(self, unit, bonus: int = 1):
        super().__init__(unit)
        self._bonus = bonus

    @property
    def power(self):
        return self.wrapped_unit.power + self._bonus

# --- Part 1: 모든 유닛의 청사진 (Subject: 옵저버 패턴 포인트 포함) ---
class Unit(ABC):
    def __init__(self, name, hp, power, attack_strategy: AttackStrategy = None):
        self.name = name
        self.max_hp = hp
        self._hp = hp  # 미션 2: 내부용 변수로 변경
        self.power = power
        self.is_alive = True
        self.is_lockdown = False
        self.attack_strategy: AttackStrategy = attack_strategy
        # --- 옵저버 패턴: 구독자 보관 ---
        self._observers = set()

    # 옵저버 등록/해제/알림
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.add(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: str):
        # 방어적 복사 후 알림
        for ob in list(self._observers):
            update = getattr(ob, "update", None)
            if callable(update):
                update(self, event)

    # --- 미션 1: 유닛 상태 보고 체계 개선 (던더 메서드) ---
    def __str__(self):
        return f"{self.name} (HP: {self.hp}/{self.max_hp})"

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', hp={self.max_hp}, power={self.power})"

    # --- 미션 2: 유닛 생명력 제어 시스템 강화 (@property) ---
    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        # 값이 0과 max_hp 사이를 벗어나지 않도록 보정
        self._hp = max(0, min(self.max_hp, value))

    # --- 미션 3: 유닛 관련 유틸리티 함수 (@staticmethod) ---
    @staticmethod
    def calculate_hits_to_kill(target_hp, attacker_power):
        if attacker_power <= 0:
            return float('inf')  # 0 이하의 공격력으로는 파괴 불가
        return (target_hp + attacker_power - 1) // attacker_power

    def move(self, x, y):
        if not self.is_alive or self.is_lockdown:
            status = "파괴되어" if not self.is_alive else "락다운 상태라"
            print(f"{self.name}은(는) {status} 이동할 수 없습니다.")
            return
        print(f"{self.name}이(가) ({x}, {y}) 위치로 이동합니다.")

    def take_damage(self, amount):
        if not self.is_alive: return
        self.hp -= amount
        print(f"{self}이(가) {amount}의 데미지를 입었습니다.")
        if self.hp <= 0:
            self.is_alive = False
            print(f"*** {self.name}이(가) 파괴되었습니다. ***")
            # --- 옵저버 알림: 사망 이벤트 ---
            self.notify("death")

    def set_strategy(self, new_strategy: AttackStrategy):
        """런타임에 공격 전략 교체"""
        self.attack_strategy = new_strategy
        print(f"[전략 변경] {self.name}의 공격 전략이 {new_strategy.__class__.__name__}(으)로 변경되었습니다.")

    def attack(self, target):
        if not self.is_alive or self.is_lockdown:
            status = "파괴되어" if not self.is_alive else "락다운 상태라"
            print(f"{self.name}은(는) {status} 공격할 수 없습니다.")
            return
        if target.is_alive:
            self._do_attack(target)

    # 전략 위임: 모든 하위 클래스가 동일하게 사용
    def _do_attack(self, target):
        if self.attack_strategy is None:
            print(f"{self.name}은(는) 공격 전략이 설정되지 않았습니다!")
            return
        self.attack_strategy.execute(self, target)

# --- 능력 믹스인(Mixin) 클래스 ---
class CloakableMixin:
    @log_ability_usage
    def cloak(self, duration=GameConfig.CLOAK_DURATION):
        if not self.is_alive: return
        cost = GameConfig.CLOAK_COST
        if hasattr(self, 'energy') and self.energy >= cost:
            self.energy -= cost
            self.is_cloaked = True
            print(f"{self.name}이(가) 클로킹을 사용합니다. ({duration}초 지속, 남은 에너지: {self.energy})")
            threading.Timer(duration, self.uncloak).start()
        else:
            print(f"{self.name}의 에너지가 부족하여 클로킹을 사용할 수 없습니다.")

    def uncloak(self):
        if hasattr(self, 'is_cloaked') and self.is_cloaked:
            self.is_cloaked = False
            print(f">>> {self.name}의 클로킹 효과가 해제되었습니다. <<<")

class RegeneratableMixin:
    def _start_regeneration_process(self):
        threading.Thread(target=self._regenerate_loop, daemon=True).start()

    def _regenerate_loop(self):
        while self.is_alive:
            time.sleep(1)
            if self.is_alive and self.hp < self.max_hp:
                self.hp += GameConfig.ZERGLING_HP_REGEN_RATE
                print(f"[재생] {self}의 HP가 회복됩니다.")

class EnergyRegeneratableMixin:
    def _start_energy_regeneration_process(self):
        threading.Thread(target=self._energy_regenerate_loop, daemon=True).start()

    def _energy_regenerate_loop(self):
        while self.is_alive:
            time.sleep(1)
            if self.is_alive and hasattr(self, 'energy') and self.energy < self.max_energy:
                self.energy += GameConfig.GHOST_ENERGY_REGEN_RATE
                print(f"[에너지 회복] {self.name}의 에너지가 회복됩니다. (현재 에너지: {self.energy}/{self.max_energy})")

# --- 종족별 유닛 구현 ---
class Marine(Unit):
    def __init__(self, name="마린", hp=GameConfig.MARINE_HP, power=GameConfig.MARINE_POWER):
        super().__init__(name, hp, power, attack_strategy=GaussRifleStrategy())

    @classmethod
    def create_elite_marine(cls, name):
        elite_hp = GameConfig.MARINE_HP + GameConfig.ELITE_MARINE_HP_BONUS
        elite_power = GameConfig.MARINE_POWER + GameConfig.ELITE_MARINE_POWER_BONUS
        return cls(name, hp=elite_hp, power=elite_power)

class Zergling(Unit, RegeneratableMixin):
    def __init__(self, name="저글링", hp=GameConfig.ZERGLING_HP, power=GameConfig.ZERGLING_POWER):
        super().__init__(name, hp, power, attack_strategy=ClawStrategy())
        self._start_regeneration_process()

class Ghost(Unit, CloakableMixin, EnergyRegeneratableMixin):
    def __init__(self, name="고스트", hp=GameConfig.GHOST_HP, power=GameConfig.GHOST_POWER):
        super().__init__(name, hp, power, attack_strategy=SniperRifleStrategy())
        self.max_energy = GameConfig.GHOST_MAX_ENERGY
        self.energy = GameConfig.GHOST_START_ENERGY
        self.is_cloaked = False
        self._start_energy_regeneration_process()

    @log_ability_usage
    def lockdown(self, target, duration=GameConfig.LOCKDOWN_DURATION):
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

            threading.Timer(duration, release_lockdown).start()
        else:
            print(f"{self.name}의 에너지가 부족하여 락다운을 사용할 수 없습니다.")

# --- 유닛 생성 팩토리 클래스 ---
class UnitFactory:
    def create_unit(self, unit_type: UnitType, name: str, **kwargs):
        if unit_type == UnitType.MARINE:
            return Marine(name=name, **kwargs)
        elif unit_type == UnitType.ZERGLING:
            return Zergling(name=name, **kwargs)
        elif unit_type == UnitType.GHOST:
            return Ghost(name=name, **kwargs)
        else:
            raise ValueError(f"'{unit_type}'은(는) 생성할 수 없는 유닛 타입입니다.")

# --- 게임 관리 클래스 (Observer) ---
class GameManager:
    def __init__(self, reporter: BattleReporter):
        self.reporter = reporter
        self.units = []
        self.unit_factory = UnitFactory()

    # 옵저버 콜백
    def update(self, unit, event: str):
        if event == "death":
            # 리스트에서 즉시 제거 (랩핑된 객체까지 고려)
            self._remove_unit_reference(unit)
            self.reporter.log(f"{unit.name}이(가) 전장에서 쓰러졌습니다. (즉시 제거됨)")

    def _remove_unit_reference(self, unit):
        # UnitDecorator에 감싸져 리스트에 들어있을 수도 있으므로 언랩 비교
        def unwrap(u):
            while isinstance(u, UnitDecorator):
                u = u.wrapped_unit
            return u
        base = unwrap(unit)
        self.units = [u for u in self.units if unwrap(u) is not base]

    def create_unit(self, unit_type: UnitType, name: str, *args, **kwargs):
        try:
            unit = self.unit_factory.create_unit(unit_type, name, *args, **kwargs)
            if unit:
                unit.attach(self)             # ✅ 생성 즉시 옵저버 등록
                self.units.append(unit)
                self.reporter.log(f"--- {unit} 생성 완료 ---")
            return unit
        except ValueError as e:
            self.reporter.log(str(e))
            return None

    def run_scenario(self):
        self.reporter.log("="*40)
        self.reporter.log("### 스타크래프트 시뮬레이터 업그레이드 작전 개시 ###")
        self.reporter.log("="*40 + "\n")

        # 1. 유닛 생성
        marine = self.create_unit(UnitType.MARINE, "용감한 마린", hp=GameConfig.SCENARIO_MARINE_HP)
        ghost = self.create_unit(UnitType.GHOST, "숙련된 고스트", hp=GameConfig.SCENARIO_GHOST_HP)
        zergling = self.create_unit(UnitType.ZERGLING, "날렵한 저글링")

        # 미션 3-1: 클래스 메서드로 정예 유닛 생성
        elite_marine = Marine.create_elite_marine("특전사 마린")
        elite_marine.attach(self)  # ✅ 수동 생성도 옵저버 등록
        self.units.append(elite_marine)
        self.reporter.log(f"--- {elite_marine} 생성 완료 ---")

        self.reporter.log("\n" + "="*30)
        self.reporter.log("### 시나리오 1: 고급 기술 테스트 ###")
        self.reporter.log("="*30)

        # 미션 2: @property 테스트
        self.reporter.log("\n--- @property 테스트 ---")
        self.reporter.log(f"고스트의 초기 HP: {ghost.hp}")
        ghost.hp += 500  # 최대 HP 이상으로 설정 시도
        self.reporter.log(f"HP 500 증가 시도 후 고스트 HP: {ghost.hp} (최대치를 넘지 않음)")

        # 미션 3-2: @staticmethod 테스트
        self.reporter.log("\n--- @staticmethod 테스트 ---")
        hits = Unit.calculate_hits_to_kill(zergling.hp, marine.power)
        self.reporter.log(f"{marine.name}이 {zergling.name}을 잡으려면 {hits}번 공격해야 합니다.")

        # 미션 4: 데코레이터 테스트
        self.reporter.log("\n--- 데코레이터 테스트 ---")
        ghost.lockdown(marine, duration=4)
        time.sleep(1)
        ghost.cloak(duration=5)

        self.reporter.log("\n" + "="*30)
        self.reporter.log("### 시나리오 2: 전투 및 자동 회복 ###")
        self.reporter.log("="*30)

        time.sleep(4)  # 락다운 및 클로킹 해제 시간 대기

        # --- (미션3) 데코레이터 패턴: 마린 무기 업그레이드(+1) 적용 ---
        self.reporter.log("\n--- 데코레이터 패턴: 마린 무기 업그레이드(+1) 적용 ---")
        marine = DamageUpgradeDecorator(marine, bonus=1)  # 변수만 감싸도 원본 유닛 옵저버는 그대로 유지
        self.reporter.log(f"업그레이드 후 {marine.name}의 공격력: {marine.power}")

        # 기본 전략으로 교전
        elite_marine.attack(zergling)
        zergling.attack(marine)

        self.reporter.log("\n저글링이 자동 회복하는 동안 대기합니다 (2초)...")
        time.sleep(2)

        # --- (도전) 전략 교체: 마린 → 스팀팩 전략 ---
        self.reporter.log("\n--- 전략 패턴: 마린이 스팀팩 전략으로 전환 ---")
        marine.set_strategy(StimpackStrategy())
        marine.attack(zergling)  # 업그레이드(+1) + 스팀팩(+6) 반영

        # 저글링을 끝까지 정리
        while zergling.is_alive:
            if elite_marine.is_alive:
                elite_marine.attack(zergling)
            time.sleep(0.5)

        # 생존 유닛 출력 (옵저버에 의해 사망자는 실시간 제거됨)
        self.reporter.log(f"\n시나리오 종료 후 생존 유닛: {[str(unit) for unit in self.units if getattr(unit, 'is_alive', False)]}")

# --- 시뮬레이션 실행 코드 ---
if __name__ == "__main__":
    reporter = ConsoleReporter()   # DIP: 구체 구현을 여기에서 주입
    game_manager = GameManager(reporter)
    game_manager.run_scenario()
