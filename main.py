"""Mini NPU Simulator: MAC 연산으로 패턴이 Cross인지 X인지 판정하는 콘솔 프로그램."""

import json
import os
import time

# ===== 설정값 (상수) =====
EPSILON = 1e-9                                            # 동점으로 볼 점수 차이의 기준 (허용오차)
LABEL_MAP = {"+": "Cross", "cross": "Cross", "x": "X"}    # 여러 라벨 표기 → 표준 라벨
REPEAT = 10                                               # 성능 측정 반복 횟수
LINE = "#" + "-" * 40                                     # 화면 구분선
COMPARE_REPEAT = 1000                                     # 보너스 2차원/1차원 비교용 반복 횟수 (두 방식 동일)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")  # main.py와 같은 폴더의 data.json


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


# ===== 보너스: 패턴 생성기 =====
def make_cross(n):
    """n×n 십자가 패턴을 만든다. 가운데 행과 가운데 열이 1.0, 나머지는 0.0."""
    mid = n // 2                                  # 가운데 위치 (n=5 → 2)
    return [[1.0 if i == mid or j == mid else 0.0 for j in range(n)] for i in range(n)]


def make_x(n):
    """n×n X 패턴을 만든다. 두 대각선(i == j, i + j == n - 1)이 1.0, 나머지는 0.0."""
    return [[1.0 if i == j or i + j == n - 1 else 0.0 for j in range(n)] for i in range(n)]


def print_matrix(matrix):
    """패턴을 ■(0이 아닌 값)와 □(0)로 그려서 보여 준다."""
    for row in matrix:
        print(" ".join("■" if v else "□" for v in row))


# ===== 보너스: 1차원 배열 최적화 =====
def flatten(matrix):
    """n×n 2차원 배열을 길이 n²의 1차원 리스트로 편다. (행 순서대로 이어 붙임)"""
    flat = []
    for row in matrix:
        flat.extend(row)                          # 한 행을 통째로 뒤에 붙임
    return flat


def mac_flat(a, b):
    """1차원 리스트 두 개를 같은 위치끼리 곱해 모두 더한다. 반복문 1개, 인덱스 1개로 접근."""
    total = 0
    for k in range(len(a)):
        total += a[k] * b[k]
    return total


# ===== 성능 측정 =====
def measure_mac(pattern, flt, repeat=REPEAT, func=mac):
    """func(기본 mac)를 repeat번 실행해 1회 평균 시간(ms)을 돌려준다. 입출력 시간은 포함하지 않는다."""
    func(pattern, flt)                            # 워밍업 1회 (첫 호출의 준비 시간이 측정에 섞이지 않게)
    start = time.perf_counter()                   # 측정 시작 (초 단위, 아주 정밀한 시계)
    for _ in range(repeat):
        func(pattern, flt)                        # 연산 함수 호출 구간만 측정
    elapsed = time.perf_counter() - start         # 걸린 전체 시간 (초)
    return elapsed / repeat * 1000                # 1회 평균, 초 → ms 변환


def print_performance_table(rows):
    """rows: [(N, 평균 시간 ms), ...] 를 크기 / 평균 시간 / 연산 횟수(N²) 표로 출력한다."""
    print("크기     평균 시간(ms) 연산 횟수(N²)")   # 한글은 화면에서 2칸을 차지해 f-string 칸 맞춤 대신 직접 맞춤
    print("-" * 40)
    for n, avg_ms in rows:
        print(f"{f'{n}×{n}':<8}{avg_ms:>14.4f}{n * n:>14}")


def run_performance(filters):
    """3×3(패턴 생성기)과 data.json의 각 크기 필터로 MAC 평균 시간을 재서 [(N, ms), ...]로 반환한다."""
    rows = [(3, measure_mac(make_cross(3), make_x(3)))]   # data.json에는 3×3 필터가 없어 생성기로 만듦
    for n in sorted(filters):                     # 5, 13, 25 순서로
        rows.append((n, measure_mac(filters[n]["Cross"], filters[n]["X"])))
    return rows


def print_summary(results):
    """모드 2 결과 목록으로 전체/통과/실패 수와 실패 케이스 목록을 출력한다."""
    failed = [r for r in results if not r["passed"]]
    print(f"총 테스트: {len(results)}개")
    print(f"통과: {len(results) - len(failed)}개")
    print(f"실패: {len(failed)}개")
    if failed:
        print()
        print("실패 케이스:")
        for r in failed:
            print(f"- {r['key']}: {r['reason']}")


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
    answer = input("필터를 자동 생성할까요? (y = A 십자가 / B X 자동 생성, 엔터 = 직접 입력): ")
    if answer.strip().lower() == "y":
        filter_a = make_cross(3)                  # 보너스 패턴 생성기 재활용
        filter_b = make_x(3)
        print("필터 A (십자가)")
        print_matrix(filter_a)
        print("필터 B (X)")
        print_matrix(filter_b)
        print("✓ 필터 A, B 자동 생성 완료")
    else:
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

    print_section(f"[4] 성능 분석 (평균/{REPEAT}회)")
    print_performance_table([(3, avg_ms)])


# ===== 모드 2: data.json 분석 =====
def check_matrix(matrix, n):
    """matrix가 n×n 숫자 배열인지 검사한다. 정상이면 빈 문자열, 문제가 있으면 사유를 반환한다."""
    if not isinstance(matrix, list):
        return "2차원 배열이 아님"
    if len(matrix) != n:
        return f"행 개수 {len(matrix)}개 (필요: {n}개)"
    for i, row in enumerate(matrix):
        if not isinstance(row, list) or len(row) != n:
            count = len(row) if isinstance(row, list) else 0
            return f"{i + 1}행의 열 개수 {count}개 (필요: {n}개)"
        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return f"{i + 1}행에 숫자가 아닌 값 {value!r}"
    return ""


def load_json(path):
    """JSON 파일을 읽어 딕셔너리로 반환한다. 파일이 없거나 형식이 깨졌으면 안내 후 None."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ 파일을 찾을 수 없습니다: {path}")
    except json.JSONDecodeError as e:
        print(f"✗ JSON 형식 오류: {e}")
    return None


def get_size(key):
    """'size_5'나 'size_5_1' 같은 키에서 크기 5를 꺼낸다. 형식이 틀리면 None."""
    if not key.startswith("size_"):           # 'size_'로 시작해야 함
        return None
    try:
        return int(key.split("_")[1])          # '_'로 자른 두 번째 조각을 숫자로
    except ValueError:                         # 숫자가 아니면 (예: size_abc)
        return None


def load_filters(data):
    """data['filters']를 읽어 {N: {'Cross': 배열, 'X': 배열}} 형태로 반환한다.
    필터 키(cross, x)는 표준 라벨로 정규화하고, 크기가 맞지 않는 필터는 건너뛴다."""
    filters = {}
    raw = data.get("filters")
    if not isinstance(raw, dict):
        print("✗ data.json에 filters 항목이 없거나 형식이 잘못되었습니다.")
        return filters

    for size_key, group in raw.items():
        n = get_size(size_key)
        if n is None or not isinstance(group, dict):
            print(f"✗ {size_key}: 필터 키 형식 오류 (size_N 형태가 아님) → 건너뜀")
            continue

        loaded = {}
        for label_key, matrix in group.items():
            label = normalize_label(label_key)              # 'cross' → Cross, 'x' → X
            if label is None:
                print(f"✗ {size_key}.{label_key}: 알 수 없는 필터 라벨 → 건너뜀")
            elif check_matrix(matrix, n):
                print(f"✗ {size_key}.{label_key}: {check_matrix(matrix, n)} → 건너뜀")
            else:
                loaded[label] = matrix

        if "Cross" in loaded and "X" in loaded:
            filters[n] = loaded
            print(f"✓ {size_key:<7} 필터 로드 완료 (Cross, X)")
        else:
            print(f"✗ {size_key}: Cross와 X 필터가 모두 있어야 합니다 → 이 크기는 사용 불가")
    return filters


def analyze_pattern(key, item, filters):
    """패턴 하나를 검증·판정해 결과 딕셔너리를 반환한다. 문제가 있으면 FAIL과 사유를 남긴다."""
    result = {"key": key, "cross": None, "x": None, "verdict": None,
              "expected": None, "passed": False, "reason": ""}

    n = get_size(key)
    if n is None:
        result["reason"] = "패턴 키 형식 오류 (size_N_idx 형태가 아님)"
        return result
    if n not in filters:
        result["reason"] = f"size_{n} 필터가 없음"
        return result
    if not isinstance(item, dict):
        result["reason"] = "패턴 항목 형식 오류"
        return result

    expected = normalize_label(item.get("expected"))         # '+' → Cross, 'x' → X
    if expected is None:
        result["reason"] = f"expected 라벨 오류 ({item.get('expected')!r})"
        return result
    result["expected"] = expected

    pattern = item.get("input")
    problem = check_matrix(pattern, n)
    if problem:
        result["reason"] = f"크기/형식 불일치: 필터는 {n}×{n}인데 패턴은 {problem}"
        return result

    result["cross"] = mac(pattern, filters[n]["Cross"])
    result["x"] = mac(pattern, filters[n]["X"])
    result["verdict"] = judge(result["cross"], result["x"], "Cross", "X")

    if result["verdict"] == expected:
        result["passed"] = True
    elif result["verdict"] == "UNDECIDED":
        result["reason"] = "동점(UNDECIDED) 처리 규칙에 따라 FAIL"
    else:
        result["reason"] = f"판정 {result['verdict']} ≠ expected {expected}"
    return result


def print_pattern_result(r):
    """패턴 하나의 분석 결과를 출력한다."""
    print(f"--- {r['key']} ---")
    if r["verdict"] is None:                                  # 검증 단계에서 걸린 경우
        print(f"FAIL ({r['reason']})")
        return
    print(f"Cross 점수: {r['cross']}")
    print(f"X 점수: {r['x']}")
    status = "PASS" if r["passed"] else f"FAIL ({r['reason']})"
    print(f"판정: {r['verdict']} | expected: {r['expected']} | {status}")


def run_mode2(path=DATA_FILE):
    """모드 2: data.json의 필터와 패턴을 읽어 일괄 판정하고 결과 목록을 반환한다."""
    data = load_json(path)
    if data is None:
        return []

    print_section("[1] 필터 로드")
    filters = load_filters(data)

    print_section("[2] 패턴 분석 (라벨 정규화 적용)")
    patterns = data.get("patterns")
    if not isinstance(patterns, dict):
        print("✗ data.json에 patterns 항목이 없거나 형식이 잘못되었습니다.")
        return []

    results = []
    for key, item in patterns.items():
        r = analyze_pattern(key, item, filters)
        print_pattern_result(r)
        results.append(r)

    print_section(f"[3] 성능 분석 (평균/{REPEAT}회)")
    print_performance_table(run_performance(filters))

    print_section("[4] 결과 요약")
    print_summary(results)
    return results


# ===== 모드 3: 보너스 =====
def read_size(low=3, high=51, default=5):
    """패턴 크기 N을 입력받는다. 엔터면 기본값, 범위 밖이거나 숫자가 아니면 다시 묻는다."""
    while True:
        text = input(f"크기 N 입력 ({low}~{high}, 엔터 = {default}): ").strip()
        if text == "":
            return default
        try:
            n = int(text)
        except ValueError:
            print(f"입력 형식 오류: 정수를 입력하세요. ('{text}')")
            continue
        if low <= n <= high:
            return n
        print(f"입력 범위 오류: {low}부터 {high} 사이의 정수를 입력하세요.")


def run_bonus():
    """모드 3: 패턴 생성기로 N×N 패턴을 만들고, 2차원/1차원 MAC 성능을 비교한다."""
    print_section("[1] 패턴 생성기")
    n = read_size()
    cross, x = make_cross(n), make_x(n)
    if n <= 15:                                   # 너무 크면 화면을 넘치므로 15×15까지만 그림
        print(f"\n{n}×{n} 십자가 (Cross)")
        print_matrix(cross)
        print(f"\n{n}×{n} X")
        print_matrix(x)
    print()
    for name, pattern, label in (("십자가 패턴", cross, "Cross"), ("X 패턴", x, "X")):
        score_c, score_x = mac(pattern, cross), mac(pattern, x)
        verdict = judge(score_c, score_x, "Cross", "X")
        mark = "✓" if verdict == label else "✗"
        print(f"{name}: Cross 점수 {score_c} / X 점수 {score_x} → 판정 {verdict} {mark}")

    print_section(f"[2] 1차원 배열 최적화 비교 (동일 입력, 각 {COMPARE_REPEAT}회 평균)")
    print("크기     2차원(ms)   1차원(ms)   시간 감소   점수 일치")
    print("-" * 56)
    for size in sorted({3, 5, 13, 25, n}):        # 과제 크기 4종 + 입력한 N (중복 제거)
        a, b = make_cross(size), make_x(size)     # 같은 입력을
        fa, fb = flatten(a), flatten(b)           # 1차원으로 미리 펴 둠 (변환 시간은 측정에서 제외)
        t2 = measure_mac(a, b, COMPARE_REPEAT)
        t1 = measure_mac(fa, fb, COMPARE_REPEAT, mac_flat)
        same = "✓" if mac(a, b) == mac_flat(fa, fb) else "✗"
        print(f"{f'{size}×{size}':<8}{t2:>10.4f}{t1:>12.4f}{(t2 - t1) / t2 * 100:>11.1f}%{same:>8}")


# ===== 메인 =====
def main():
    """시작 화면과 모드 선택 메뉴. 1, 2, 3이 아니면 다시 묻는다."""
    print("=== Mini NPU Simulator ===")
    while True:
        print()
        print("[모드 선택]")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        print("3. 보너스: 패턴 생성기 + 1차원 최적화 비교")
        choice = input("선택: ").strip()
        if choice == "1":
            run_mode1()
            break
        elif choice == "2":
            run_mode2()
            break
        elif choice == "3":
            run_bonus()
            break
        else:
            print("1, 2, 3 중에서 입력하세요.")


if __name__ == "__main__":
    main()
