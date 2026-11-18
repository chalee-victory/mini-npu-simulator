"""Mini NPU Simulator: MAC 연산으로 패턴이 Cross인지 X인지 판정하는 콘솔 프로그램."""

import time

# ===== 설정값 (상수) =====
EPSILON = 1e-9                                            # 동점으로 볼 점수 차이의 기준 (허용오차)
LABEL_MAP = {"+": "Cross", "cross": "Cross", "x": "X"}    # 여러 라벨 표기 → 표준 라벨
REPEAT = 10                                               # 성능 측정 반복 횟수
LINE = "#" + "-" * 40                                     # 화면 구분선


# ===== 핵심 함수 =====
def mac(pattern, flt):
    """입력 패턴과 필터를 같은 위치끼리 곱한 뒤 모두 더한 점수를 돌려준다."""
    total = 0
    n = len(pattern)                              # 행의 개수 (N×N이므로 열 개수와 같음)
    for i in range(n):                            # 행 반복
        for j in range(n):                        # 열 반복
            total += pattern[i][j] * flt[i][j]    # 같은 위치끼리 곱해서 누적
    return total


def normalize_label(label):
    """여러 표기의 라벨을 표준 라벨 Cross 또는 X로 바꾼다. 알 수 없으면 None."""
    key = str(label).strip().lower()              # 앞뒤 공백 제거 후 소문자로 통일
    return LABEL_MAP.get(key)                     # 대응표에서 찾고, 없으면 None


def judge(score_a, score_b, label_a="A", label_b="B"):
    """두 점수를 허용오차 기준으로 비교해 판정한다. 차이가 EPSILON보다 작으면 UNDECIDED."""
    if abs(score_a - score_b) < EPSILON:          # 차이가 허용오차보다 작으면 동점
        return "UNDECIDED"
    elif score_a > score_b:                       # A 점수가 더 크면 A
        return label_a
    else:                                         # 그 외에는 B
        return label_b


# ===== 성능 측정 =====
def measure_mac(pattern, flt, repeat=REPEAT):
    """mac()을 repeat번 실행해 1회 평균 시간(ms)을 돌려준다. 입출력 시간은 포함하지 않는다."""
    start = time.perf_counter()                   # 측정 시작 (초 단위, 아주 정밀한 시계)
    for _ in range(repeat):
        mac(pattern, flt)                         # 연산 함수 호출 구간만 측정
    elapsed = time.perf_counter() - start         # 걸린 전체 시간 (초)
    return elapsed / repeat * 1000                # 1회 평균, 초 → ms 변환


# ===== 모드 1: 사용자 입력 =====
def print_section(title):
    """구분선과 제목을 출력한다."""
    print()
    print(LINE)
    print(f"# {title}")
    print(LINE)


def read_matrix(name, n=3):
    """name 행렬을 n줄 입력받아 n×n float 리스트로 반환한다. 오류 시 해당 줄만 다시 입력받는다."""
    print(f"{name} ({n}줄 입력, 공백 구분)")
    matrix = []
    while len(matrix) < n:                        # 정상 줄이 n개 모일 때까지 반복 → 행 수는 항상 n
        parts = input().split()                   # 공백(여러 개여도 OK) 기준으로 나눔

        if len(parts) != n:                       # 검사 1: 열 개수
            print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요. "
                  f"(입력된 개수: {len(parts)}) → {len(matrix) + 1}번째 줄을 다시 입력하세요.")
            continue

        try:                                      # 검사 2: 숫자 변환
            row = [float(p) for p in parts]
        except ValueError:
            print(f"입력 형식 오류: 숫자가 아닌 값이 있습니다. ({' '.join(parts)}) "
                  f"→ {len(matrix) + 1}번째 줄을 다시 입력하세요.")
            continue

        matrix.append(row)                        # 두 검사를 통과한 줄만 저장
    return matrix



def run_mode1():
    """모드 1: 3×3 필터 A, B와 패턴을 입력받아 MAC 점수, 연산 시간, 판정을 출력한다."""
    print_section("[1] 필터 입력")
    filter_a = read_matrix("필터 A")
    print()
    filter_b = read_matrix("필터 B")
    print("✓ 필터 A, B 저장 완료")

    print_section("[2] 패턴 입력")
    pattern = read_matrix("패턴")
    print("✓ 패턴 저장 완료")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    avg_ms = measure_mac(pattern, filter_a)       # 3×3 MAC 1회 평균 시간
    result = judge(score_a, score_b)

    print_section("[3] MAC 결과")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/{REPEAT}회): {avg_ms:.4f} ms")
    if result == "UNDECIDED":
        print(f"판정: 판정 불가 (|A-B| < {EPSILON})")
    else:
        print(f"판정: {result}")


# ===== 메인 =====
def main():
    """시작 화면과 모드 선택 메뉴. 1 또는 2가 아니면 다시 묻는다."""
    print("=== Mini NPU Simulator ===")
    while True:
        print()
        print("[모드 선택]")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        choice = input("선택: ").strip()
        if choice == "1":
            run_mode1()
            break
        elif choice == "2":
            print("모드 2는 3단계에서 구현 예정입니다.")
            break
        else:
            print("1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()
