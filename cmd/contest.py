def read_from_data(file_name: str):
    out = []
    with open("data/" + file_name, "r") as f:
        for each in f.readlines():
            out.append(each.strip("\n"))
    return out


ENTRIES = read_from_data("en.zote")
WINNERS = read_from_data("win.zote")
WINNERS2 = read_from_data("win2.zote")


def enter_contest(u_id: str):
    try:
        if u_id not in ENTRIES:
            ENTRIES.append(u_id)
            with open("data/en.zote", "a") as f:
                f.write(u_id + "\n")
            return "added"
        else:
            return "already"
    except Exception as e:
        return "error"


def win_contest(u_id: str):
    WINNERS.append(u_id)
    with open("data/win.zote", "a") as f:
        f.write(u_id + "\n")
        print(len(WINNERS), len(ENTRIES))
    return True


def win_contest2(u_id: str):
    WINNERS2.append(u_id)
    with open("data/win2.zote", "a") as f:
        f.write(u_id + "\n")
    print(len(WINNERS2), len(ENTRIES))
    return True