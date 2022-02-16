def accept_exactly_one(**kwargs) -> bool:
    populated = False

    for _, v in kwargs.items():
        if v is not None:
            if populated:
                return False
            populated = True

    return populated
