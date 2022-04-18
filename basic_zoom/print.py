import json
from rich import print_json

# used to view results


def pretty(result):
    if type(result) == dict:
        pretty_result = json.dumps(result, indent=4)

        for item in result:
            if type(result[item]) == list:
                pretty_result = (
                    pretty_result + f"\nLength of {item} results: {len(result[item])}"
                )

        return pretty_result
    elif type(result) == list:
        return json.dumps(result, indent=4) + f"\nLength of list: {len(result)}"
    else:
        return result


def pretty_print(result):
    if type(result) == dict:
        print_json(json.dumps(result))

        for item in result:
            if type(result[item]) == list:
                print(f"\nLength of {item} results: {len(result[item])}")

    elif type(result) == list:
        print_json(json.dumps(result))
        print(f"\nLength of list: {len(result)}")
    else:
        return result
