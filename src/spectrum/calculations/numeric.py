from collections import Counter
from math import sqrt

__author__ = 'Daniel Lytkin'

# Module providing methods to calculate GCD and LCM etc.

def gcd(a, b):
    """Returns GCD of two numbers
    """
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    """Returns LCM of two numbers
    """
    return a / gcd(a, b) * b


def prime_part(n, b):
    """Returns b'-part of number n, which is the greatest divisor of n coprime to d
    """
    while True:
        d = gcd(n, b)
        if d <= 1: break
        n //= d
    return n


def filter_divisors(iterable, reverse=False):
    """
    removes all elements that divide any other.
    input argument must be in decreasing order
    If 'reverse' is True, returns list in increasing order
    """
    ret = []
    if not reverse:
        def append_left(element): ret.insert(0, element)

        add_element = append_left
    else:
        add_element = ret.append
    for element in iterable:
        if not any(x % element == 0 for x in ret):
            add_element(element)

    return ret


def sort_and_filter(sequence, reverse=False):
    """Converts raw sequence of numbers to sorted sequence without divisors
    """
    ret = list(sequence)
    ret.sort(reverse=True)
    return filter_divisors(ret, reverse=reverse)


def first_divisor(number):
    """Returns lowest divisor of 'number' greater than 1
    """
    if not number % 2: return 2
    for j in xrange(1, int(sqrt(number)) // 2 + 1):
        i = 2 * j + 1
        if number % i == 0:
            return i
    return number


def next_odd_divisor(number, previous):
    """Returns next divisor greater than 'previous'.
    Number must not be divisible by any number <= previous.
    """
    for j in xrange(previous // 2 + 1, int(sqrt(number)) // 2 + 1):
        i = 2 * j + 1
        if number % i == 0:
            return i
    return number


def get_exponent(number, base):
    """If number = base**k, returns k. Else returns None
    """
    if number <= 1: return 0
    k = 0
    if base > 1:
        while number % base == 0:
            number /= base
            k += 1
    return k if number == 1 else None


class Integer:
    """Represents integer with methods to factorize.
    Usage: Integer(12345) for number 12345 or Integer((2,5), (3,2), 5, 7) for number 2^5 * 3^3 * 5 * 7
    """

    def __init__(self, *args):
        if len(args) == 1:
            if type(args[0]) in (int, long):
                self._int = args[0]
                self._factors = None
            if isinstance(args[0], Integer):
                self._int = args[0]._int
                self._factors = args[0]._factors
        else:
            self._factors = Counter()
            for arg in args:
                if type(arg) in (int, long):
                    self._factors[arg] += 1
                else:
                    if arg[1]: self._factors[arg[0]] += arg[1]
            self._int = reduce(lambda x, y: x * y, self._factors.elements())


    def __int__(self):
        return self._int

    def __cmp__(self, other):
        if isinstance(other, Integer):
            return cmp(self._int, other._int)
        return cmp(self._int, other)

    @staticmethod
    def _removeFactor(number, factor):
        power = 0
        while number % factor == 0:
            number /= factor
            power += 1
        return power, number

    @property
    def factors(self):
        if self._factors is None:
            self._factors = Counter()
            # first handle the 2 for other primes are odd, thus we can then increment divisor by two
            power, remainder = Integer._removeFactor(self._int, 2)
            if power:
                self._factors[2] += power

            currentDivisor = 1
            while remainder > 1:
                # search for the next divisor
                currentDivisor = next_odd_divisor(remainder, currentDivisor)
                # and remove it
                power, remainder = Integer._removeFactor(remainder,
                    currentDivisor)
                if power:
                    self._factors[currentDivisor] += power

        return self._factors