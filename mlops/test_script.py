def add_numbers(a: int, b: int) -> int:
    return a + b


def greet_user(name: str) -> str:
    return f"Hello, {name}!"


if __name__ == "__main__":
    result = add_numbers(5, 3)
    print(result)
    greeting = greet_user("Alice")
    print(greeting)
