from abc import ABC, abstractmethod
import random
import time

class EnergyPool:
    def __init__(self, current=0, maximum=200, basic_amount = 0):
        self.current = current
        self.maximum = maximum
        self.basic_amount = basic_amount
    
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

    def update(self):
        if self.basic_amount <= 0:
            return 0
        
        before = self.current
        self.current = min(self.maximum, self.current + self.basic_amount)
        
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
        if not self.owner.can_act():
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
    def __init__(self, owner, amount):
        self.owner = owner
        self.amount = amount
    
    def regenerate(self):
        if not self.owner.can_act():
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
    
    def is_alive(self):
        return self.hp > 0
    
    def move(self, nx, ny):
        self.x, self.y = nx, ny
    
    def can_act(self):
        return self.is_alive()
    
    def attacked(self, dmg):
        if not self.is_alive():
            return
        
        self.hp = max(self.hp - dmg, 0)
        
        if self.hp == 0:
            print(f"Unit {self.name}이(가) 사망하였습니다.")
    
    @abstractmethod
    def attack(self, other):
        pass
    
    def update(self):
        pass

class GroundUnit(BaseUnit, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ground_unit = True
    
    def update(self, **kwargs):
        super().update()

class AerialUnit(BaseUnit, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.air_unit = True
    
    def update(self, **kwargs):
        super().update()

class MechanicUnit(BaseUnit, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.islockdown = False
        self.locktick = 0
    
    def _islockdown(self):
        if self.islockdown:
            return True
        return False
    
    def can_act(self):
        return super().can_act() and not self._islockdown()
    
    def update(self, **kwargs):
        super().update()
        
        if self.locktick > 0:
            self.locktick -= 1
            
            if self.locktick == 0:
                self.islockdown = False
                print(f"{self.name}의 락다운이 해제되었습니다.")

class CreatureUnit(BaseUnit, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def can_act(self):
        return super().can_act()
    
    def update(self, **kwargs):
        super().update()

class Marine(GroundUnit, MechanicUnit):
    def __init__(self, hp=100, x=0, y=0, name="Default Marine"):
        super().__init__(hp=hp, x=x, y=y, name=name)
        self.gauss_dmg = 12
        
    def attack(self, other):
        if not super().can_act():
            return
        
        other.attacked(self.gauss_dmg)
        print(f"{self.name}: 가우스 소총 발사! ({self.gauss_dmg} 피해)")
    
    def update(self):
        super().update()

class Zergling(GroundUnit, CreatureUnit):
    def __init__(self, hp=100, x=0, y=0, name="Default Zergling"):
        super().__init__(hp=hp, x=x, y=y, name=name)
        self.claw_dmg = 10
        
        self.regen = RegenerationModule(owner=self, amount=1)
    
    def attack(self, other):
        if not super().can_act():
            return
        
        other.attacked(self.claw_dmg)
        print(f"{self.name}: 발톱으로 할퀴기! ({self.claw_dmg} 피해)")
    
    def regenerate(self):
        self.regen.regenerate()
    
    def update(self):
        super().update()
        self.regen.update()

class Zealot(GroundUnit, MechanicUnit):
    def __init__(self, hp=100, x=0, y=0, name="Default Zealot"):
        super().__init__(hp=hp, x=x, y=y, name=name)
        self.psionic_blade_dmg = 20
        
    def attack(self, other):
        if not super().can_act():
            return
        
        other.attacked(self.psionic_blade_dmg)
        print(f"{self.name}: 사이오닉 검으로 공격! ({self.psionic_blade_dmg} 피해)")
    
    def update(self):
        super().update()

class Ghost(GroundUnit, MechanicUnit):
    DEFAULT_ENERGY = 50
    MAX_ENERGY = 200
    THRESHOLD = 100
    LOCKDOWN_TICKS = 3
    BASIC_AMOUNT = 25
    
    def __init__(self, hp=100, x=0, y=0, name="Default Ghost"):
        super().__init__(hp=hp, x=x, y=y, name=name)
        self.pistol_dmg = 8
        
        self.energy = EnergyPool(current=Ghost.DEFAULT_ENERGY, maximum=Ghost.MAX_ENERGY, basic_amount=Ghost.BASIC_AMOUNT)
        self.cloaking = CloakModule(owner=self, energy_pool=self.energy,
                                    activation_cost=25, drain_per_turn=10, duration=3)
        
    def attack(self, other):
        if not super().can_act():
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
        super().update()
        self.energy.update()
        self.cloaking.update()

class Wraith(AerialUnit, MechanicUnit):
    DEFAULT_ENERGY = 60
    MAX_ENERGY = 200
    BASIC_AMOUNT = 20
    
    def __init__(self, hp=120, x=0, y=0, name="Default Wraith"):
        super().__init__(hp=hp, x=x, y=y, name=name)
        self.laser_dmg = 14
        
        self.energy = EnergyPool(current=Wraith.DEFAULT_ENERGY, maximum=Wraith.MAX_ENERGY, basic_amount=Wraith.BASIC_AMOUNT)
        self.cloaking = CloakModule(owner=self, energy_pool=self.energy,
                                    activation_cost=25, drain_per_turn=12, duration=3)
    
    def attack(self, other):
        if not super().can_act():
            return
        
        other.attacked(self.laser_dmg)
        print(f"{self.name}: 듀얼 레이저 발사! ({self.laser_dmg} 피해)")
        
    def cloak(self):
        self.cloaking.cloak()
        
    def uncloak(self):
        self.cloaking.uncloak("수동 해제")
        
    def update(self):
        super().update()
        self.energy.update()
        self.cloaking.update()

class Game:
    def __init__(self, players, max_turns=12, seed=None,
                p_lockdown=0.35, p_cloak=0.25, p_uncloak=0.10, verbose=True):
        """
        players: [team1_units, team2_units, ...]
        max_turns: 최대 턴 수
        seed: 랜덤 시드 (재현용)
        p_lockdown: 고스트가 락다운을 시도할 확률 (조건 충족 시)
        p_cloak: 유닛이 은폐를 시도할 확률 (조건 충족 시)
        p_uncloak: 은폐 중 해제를 시도할 확률
        verbose: 출력 on/off
        """
        self.players = players
        self.max_turns = max_turns
        self.p_lockdown = p_lockdown
        self.p_cloak = p_cloak
        self.p_uncloak = p_uncloak
        self.verbose = verbose

        if seed is not None:
            random.seed(seed)

        self.all_units = [u for team in players for u in team]
        self.unit_team = {u: i for i, team in enumerate(players) for u in team}

    # ========== 헬퍼 ==========
    def _alive_units(self):
        return [u for u in self.all_units if u.is_alive()]

    def _alive_enemies(self, unit):
        tid = self.unit_team[unit]
        return [e for e in self._alive_units() if self.unit_team[e] != tid]

    def _print(self, msg):
        if self.verbose:
            print(msg)

    # ========== 액션 결정 ==========
    def _act(self, u):
        if not u.can_act():
            return
        enemies = self._alive_enemies(u)
        if not enemies:
            return

        # 고스트: 락다운/클로킹/공격
        if isinstance(u, Ghost):
            mech_targets = [e for e in enemies if isinstance(e, MechanicUnit)]
            if (u.energy.current >= Ghost.THRESHOLD and mech_targets
                    and random.random() < self.p_lockdown):
                target = random.choice(mech_targets)
                u.lockdown(target)
                return

            # 클로킹 토글 혹은 공격
            if (not u.cloaking.is_cloaked
                and u.energy.current >= u.cloaking.activation_cost
                and random.random() < self.p_cloak):
                u.cloak()
            elif u.cloaking.is_cloaked and random.random() < self.p_uncloak:
                u.uncloak()
            else:
                u.attack(random.choice(enemies))
            return

        # 레이스: 클로킹 토글/공격
        if isinstance(u, Wraith):
            if (not u.cloaking.is_cloaked
                and u.energy.current >= u.cloaking.activation_cost
                and random.random() < self.p_cloak):
                u.cloak()
            elif u.cloaking.is_cloaked and random.random() < self.p_uncloak:
                u.uncloak()
            else:
                u.attack(random.choice(enemies))
            return

        # 그 외: 공격
        u.attack(random.choice(enemies))

    # ========== 한 턴 진행 ==========
    def step(self, turn_index):
        self._print(f"\n=== Turn {turn_index} ===")
        acting = self._alive_units()
        random.shuffle(acting)
        for u in acting:
            self._act(u)

        # 턴 종료 업데이트
        for u in self.all_units:
            u.update()

    # ========== 종료/승패 판정 ==========
    def _alive_team_ids(self):
        return {self.unit_team[u] for u in self.all_units if u.is_alive()}

    def is_over(self):
        alive = self._alive_team_ids()
        return len(alive) <= 1

    def winner(self):
        alive = self._alive_team_ids()
        if len(alive) == 1:
            return next(iter(alive))  # team index
        return None  # 무승부 또는 아직 진행 중

    # ========== 전체 실행 ==========
    def run(self):
        for t in range(1, self.max_turns + 1):
            if self.is_over():
                break
            self.step(t)

        if self.is_over():
            w = self.winner()
            if w is None:
                self._print("\n== 전원 전멸. 무승부 ==")
            else:
                self._print(f"\n== Team {w+1} 승리! ==")
        else:
            self._print("\n== 턴 제한으로 종료 ==")

if __name__ == "__main__":
    player1 = [Marine(100, 0, 0, "Marine1"),
               Marine(100, 1, 1, "Marine2"),
               Marine(100, 2, 2, "Marine3"),
               Ghost(100, 3, 3, "Ghost1")]

    player2 = [Zergling(100, 0, 5, "Zergling1"),
               Zergling(100, 1, 6, "Zergling2"),
               Zergling(100, 2, 7, "Zergling3")]

    player3 = [Zealot(100, 0, 10, "Zealot1"),
               Zealot(100, 0, 20, "Zealot2")]
    
    player4 = [Wraith(120, 5, 5, "Wraith1"),
               Wraith(120, 7, 7, "Wraith2")]

    players = [player1, player2, player3, player4]

    game = Game(players, max_turns=50, seed=time.time(),
                p_lockdown=0.35, p_cloak=0.25, p_uncloak=0.10, verbose=True)

    game.run()