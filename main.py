"""Mini NPU Simulator: MAC 연산으로 패턴이 Cross인지 X인지 판정하는 콘솔 프로그램."""

# ===== 설정값 (상수) =====
EPSILON = 1e-9                                            # 동점으로 볼 점수 차이의 기준 (허용오차)
LABEL_MAP = {"+": "Cross", "cross": "Cross", "x": "X"}    # 여러 라벨 표기 → 표준 라벨


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

"""
# ===== 임시 테스트 (확인 후 정리 예정) =====
cross = [[0, 1, 0],
         [1, 1, 1],
         [0, 1, 0]]
x_flt = [[1, 0, 1],
         [0, 1, 0],
         [1, 0, 1]]

print(mac(cross, cross))    # 예상: 5
print(mac(cross, x_flt))    # 예상: 1
print(mac(x_flt, x_flt))    # 예상: 5
print(mac([[0.5, 0.4], [0.0, 0.0]], [[1, 1], [1, 1]]))   # 예상: 0.9

print(normalize_label("+"))        # 예상: Cross
print(normalize_label("cross"))    # 예상: Cross
print(normalize_label("x"))        # 예상: X
print(normalize_label(" X "))      # 예상: X
print(normalize_label("Cross"))    # 예상: Cross
print(normalize_label("circle"))   # 예상: None

print(judge(5, 1))                          # 예상: A
print(judge(1, 5))                          # 예상: B
print(judge(5, 1, "Cross", "X"))            # 예상: Cross
print(judge(1, 5, "Cross", "X"))            # 예상: X
print(judge(1, 1))                          # 예상: UNDECIDED
print(judge(0.9, 0.8999999999999999))       # 예상: UNDECIDED  (부동소수점 동점)
print(0.9 > 0.8999999999999999)             # 참고: True  (그냥 비교하면 A가 이긴 것으로 나옴)
"""