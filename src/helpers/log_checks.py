from models.feedback import FeedbackGroup, FeedbackLevel, Feedback, FeedbackCollection


def check_log(log_json, account_name) -> FeedbackCollection:
    fbc = FeedbackCollection()

    # General log checks
    fbg_valid = FeedbackGroup(message="Checking if log is valid")
    fbc.add(fbg_valid)

    for player in log_json["players"]:
        if player['account'] == account_name:
            break
    else:
        fbg_valid.add(Feedback(f"Could not find account {account_name} in log", FeedbackLevel.ERROR))
    # TODO: check version, boss allowed...

    # General performance checks
    fbg_general = FeedbackGroup(message="Checking performance")
    fbc.add(fbg_general)

    if not log_json["success"]:
        fbg_general.add(Feedback("Boss was not killed", FeedbackLevel.ERROR))

    squad_downs = 0
    squad_deaths = 0
    found_blood_magic = False
    is_emboldened = False
    for player in log_json["players"]:
        if player["account"] == account_name:
            if player["defenses"][0]["deadCount"] > 0 > 0:
                fbg_general.add(Feedback(f"You've died. You must be alive at the end of the fight.", FeedbackLevel.ERROR))

        squad_downs += player["defenses"][0]["downCount"]
        squad_deaths += player["defenses"][0]["deadCount"]

        for b in player["buffUptimes"]:
            if b["id"] == 29726:
                found_blood_magic = True
            if b["id"] == 68087:
                is_emboldened = True

    if squad_downs > 9:
        fbg_general.add(Feedback(f"Your squad has a lot of downs. ({squad_downs})", FeedbackLevel.WARNING))

    if squad_deaths > 2:
        fbg_general.add(Feedback(f"Your squad has a lot of deaths. ({squad_deaths})", FeedbackLevel.WARNING))

    if found_blood_magic:
        fbg_general.add(Feedback(f"We do not allow logs with a Blood Magic Necromancer present.", FeedbackLevel.ERROR))

    if is_emboldened:
        fbg_general.add(Feedback(f"We do not allow logs with Emboldened Mode active.", FeedbackLevel.ERROR))

    return fbc