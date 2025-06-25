import typer, re
import pandas as pd
import random
import json
import copy


app = typer.Typer()
def generate_random_number(min_val=0, max_val=1000000):
    return random.randint(min_val, max_val)

def line_check(line, dictionary):
    lower_line = line.lower()
    for word in dictionary:
        match_word = re.compile(word)
        # print("Sub match: ", dictionary[word]['Sub Match Condition'])

        sub_match = re.compile(dictionary[word]['Sub Match Condition'])
        if match_word.search(lower_line):
            # print("Found it", line)
            # print(dictionary[word])
            print(f"line match found: {lower_line}")
            if dictionary[word]['Sub Match Condition']:
                print(f"Additional Match condition Detected: {dictionary[word]['Sub Match Condition']}")
                if sub_match.fullmatch(lower_line):
                    capture = sub_match.fullmatch(lower_line)
                    # value = capture.group(1)
                    print(f"Additional condition matched: {lower_line}")
                    # print(f"Captured value {value}")
                    return restructue_json(dictionary, word)
                else:
                    pass
            else:
                return restructue_json(dictionary, word)


# def detect_postman(line, dictionary):
#     low_line = line.lower()
#     for word in dictionary:
#         if dictionary[word]["Postman API"]:
#             match_word = re.compile(word)
#             sub_match = re.compile(dictionary[word]['Sub Match Condition'])
#             if dictionary[word]['Sub Match Condition'] == "":
#                 if match_word.search(low_line):
#                     return True
#             elif sub_match.fullmatch(low_line):
#                 return True
#         else:
#             return False



def restructue_json(json_dictionary, k):
    restructured_json = {
        "Configuration": k,
        "Sub Match Condition": json_dictionary[k]["Sub Match Condition"],
        "comments": json_dictionary[k]["comments"],
        "Profile Category": json_dictionary[k]["Profile Category"],
        "Profile Name": json_dictionary[k]["Profile Name"],
        "API Name": json_dictionary[k]["API Name"],
        "Configuration Method": json_dictionary[k]["Configuration Method"],
        "API Documentation": json_dictionary[k]["API Documentation"]

        }
    return restructured_json



file_id = generate_random_number()


@app.command()
def config_inspector(sw_config: str = typer.Option(..., help="Path to the switch configuration file"),
    output_file: str = typer.Option(f"output_file_{file_id}.xlsx", help="Path to the output file. By default, this tool uses the directory from which it is executed."),
    no_match_file: str = typer.Option(f"non_matched_lines_{file_id}.txt", help="Path to the file for non-matched lines. By default, the tool uses the directory from which it is executed."),
):
    """
    Inspects switch configuration file and output results to excel sheet.
    All lines without a match will be output to a text file.
    """
    initilize_excel = {
        "Configuration": "",
        "Sub Match Condition": "",
        "Matched Line": "",
        "Times Found": "",
        "comments": "",
        "Profile Category": "",
        "Profile Name": "",
        "Configuration Method": "",
        "API Name": "",
        "API Documentation": ""

        # 'In Interface Context': ""
    }
    df = pd.DataFrame(columns=initilize_excel.keys())
    feature_dictionary = pd.read_json("feature_dictionary.json")
    found_lines = []
    result_dictionary = {}
    uncaptured_lines = ""



    with open(sw_config, 'r') as file:
        lines = file.readlines()
        config_dict = {}
        for i, line in enumerate(lines):
            if not line.startswith(' '):  # Detect top-level configuration lines
                sub_config_lines = []
                j = i + 1
                while j < len(lines) and lines[j].startswith(' ' * 3):
                    sub_config_lines.append(lines[j].strip())
                    j += 1
                config_dict[line.strip()] = sub_config_lines
                # print(f"Line '{line.strip()}' has sub-configuration: {sub_config_lines}")


    for line, sub_config in config_dict.items():
        print(f"Line: {line}, {sub_config}")

        if line not in found_lines:
            word_found = line_check(line, feature_dictionary)
            # print('What is it ',type(word_found))
            if isinstance(word_found, dict):
                found_lines.append(line)
                word_found['Matched Line'] = line
                word_found['Times Found'] = 1
                shell_dict = {line: word_found}
                result_dictionary.update(shell_dict)

            else:
                print(f"No Match found logging '{line}' to file. ")
                uncaptured_lines += line + "\n"
        else:
            result_dictionary[line]['Times Found'] += 1

        for sub_line in sub_config:
            if sub_line not in found_lines:
                sub_word_found = line_check(sub_line, feature_dictionary)
                if isinstance(sub_word_found, dict):
                    found_lines.append(sub_line)
                    sub_word_found['Matched Line'] = sub_line
                    sub_word_found['Times Found'] = 1
                    shell_dict = {sub_line: sub_word_found}
                    result_dictionary.update(shell_dict)
                else:
                    print(f"No Match found logging '{sub_line}' to file. ")
                    uncaptured_lines += sub_line + "\n"
            else:
                result_dictionary[sub_line]['Times Found'] += 1


    for results in result_dictionary:
        next_df_row = len(df) + 1
        print("results", results)
        df.loc[next_df_row] = result_dictionary[results]

    df.to_excel(output_file, index=False)

    with open(no_match_file, "w") as file:
        file.write(uncaptured_lines)





#======================================================================================================================


def postman_folder_creation(postman_db, api_name, postman_call_name):
    # In postman there are folders for each set of features to keep them organized. This function searches each
    # folder if the API name matches it then searches to find the matching API call. finally it returns the API
    # folder and the call as a copy. The folder copy will only be used one time the API copy could be used multiply
    # times. Currently, NTP only has one item in its folder, so we grab that list item TO make it more scalable we
    # can actually, Match based on the api name

    match_name = re.compile(postman_call_name)
    for feature in postman_db:
        folder = feature['name']
        if folder == api_name:

            for calls in feature.get('item'):
               if match_name.search(calls['name']):
                api_call = copy.deepcopy(feature.get('item')[0])
                clean_folder = copy.deepcopy(feature)
                clean_folder['item'] = []

                return clean_folder, api_call

# This needs to return the API name also
def detect_postman(line, dictionary):
    # This function detects if the current line in the config file has a postman API call if It does have a Postman
    # call then we return the parser information and API name this API name will be used in the
    # postman_folder_creation function to determine what API folder needs to be retrieved The parser is a database
    # that will identify what values should be matched and replaced when we retrieve the API call from the Postman
    # database.
    low_line = line.lower()
    for word in dictionary:
        if dictionary[word]["Postman API"]:
            match_word = re.compile(word)
            sub_match = re.compile(dictionary[word]['Sub Match Condition'])
            if dictionary[word]['Sub Match Condition'] == "":
                if match_word.search(low_line):
                    return True, dictionary[word]['parser'], dictionary[word]['API Name'], dictionary[word]['Postman Call']
            elif sub_match.fullmatch(low_line):
                return True, dictionary[word]['parser'], dictionary[word]['API Name'], dictionary[word]['Postman Call']
    return False

def update_api_description(api_call, cli_line):
    # for any additonal configuration lines that were not initially added to the description we will add them here.
    if "{{profile_description}}" not in api_call['request']['body']['raw']:
        pattern = re.compile(r'("description":\s*")([^"]*)(")')
        match = pattern.search(api_call['request']['body']['raw'])
        if match:
            current_description = match.group(2)
            updated_description = current_description + f" {cli_line}"
            api_call['request']['body']['raw'] = pattern.sub(f'\\1{updated_description}\\3',
                                                             api_call['request']['body']['raw'])

            print(f"Updated description: {updated_description}")
        return api_call
    return api_call



def customize_api_call(parse_data, api_call, cli_line, api_name):
    # This function uses information from retrieved from the detect_postman and postman_folder_creation functions.
    # This looks through the parsed data identifies the values that need to be replaced and replaces them with the
    # Regex look up value or the value identified in the parse data.

    # for any additonal configuration lines that were not initially added to the description we will add them here.
    # if "{{profile_description}}" not in api_call['request']['body']['raw']:
    #     pattern = re.compile(r'("description":\s*")([^"]*)(")')
    #     match = pattern.search(api_call['request']['body']['raw'])
    #     if match:
    #         current_description = match.group(2)
    #         updated_description = current_description + f" {cli_line}"
    #         api_call['request']['body']['raw'] = pattern.sub(f'\\1{updated_description}\\3',
    #                                                          api_call['request']['body']['raw'])
    #
    #         print(f"Updated description: {updated_description}")






    # break into two loops  one for the patterns one for the description
    for parse_value in parse_data:
        if parse_value == "profile details":
            for details in parse_data[parse_value]:
                if details == "{{profile_name}}":
                    api_call['request']['body']['raw'] = api_call['request']['body']['raw'].replace(details, f"{api_name}_{generate_random_number()}")
                elif details == "{{profile_description}}":
                    api_call['request']['body']['raw'] = api_call['request']['body']['raw'].replace(details,
                                                                                                    f"Matched line: {cli_line.strip()}")
        if parse_value == "patterns":
            for pattern in parse_data[parse_value]:
                for key, values in pattern.items():
                    # print('values', values)
                    # print(values['pattern'])
                    # print(values['group'])
                    # print(values['replace'])
                    # print(f"what is this {type(api_call)}")
                    if values['pattern']:
                        search = re.match(values['pattern'], cli_line)
                        print(f"Values: {values}")
                        if search:
                            if 'group' in values:
                                group = values['group']
                                replace_value = str(values['replace'])
                                print(f"Group found {search.group(group)}, cli line: {cli_line}")
                                local_value = search.group(group)
                                api_call['request']['body']['raw'] = api_call['request']['body']['raw'].replace(
                                    replace_value, local_value)
                            elif 'static_value' in values:
                                print(f"Static value found {values['static_value']}, cli line: {cli_line}")
                                replace_value = str(values['replace'])
                                static_value = str(values['static_value'])
                                api_call['request']['body']['raw'] = api_call['request']['body']['raw'].replace(
                                    replace_value, static_value)
                    elif 'static_value' in values:
                        print(f"Static value found {values['static_value']}, cli line: {cli_line}")
                        replace_value = str(values['replace'])
                        static_value = str(values['static_value'])
                        api_call['request']['body']['raw'] = api_call['request']['body']['raw'].replace(replace_value,
                                                                                                        static_value)
    # print(f"Updated API call: {api_call['request']['body']['raw']}")
    return api_call

def find_key(data, key_to_find):
    # This function was an easy way to find and return values that are in the custom postman dictionary.
    # It is used to check and see if a folder has already been created.
    name_values = []
    for value in data.values():
        if isinstance(value, dict) and key_to_find in value:
            name_values.append(value['name'])
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and 'name' in item:
                    name_values.append(item['name'])
    return name_values





@app.command()
def create_collection(sw_config: str = typer.Option(..., help="Path to the switch configuration file"),
    custom_postman_collection: str = typer.Option(f"postman_collection_{file_id}.json")):

    spacer = '========================================================================================'
    with open('postman-database.json', 'r') as file:
        data = json.load(file)
    profiles = data.get("item")
    custom_postman = copy.deepcopy(data)
    custom_postman.update({'item': []})
    custom_postman['item'].append(profiles[0])
    custom_postman['item'].append(profiles[1])
    single_call = ['switch-system']
    line_matched = []
    interface_context = re.compile(r'^interface')
    with open('feature_dictionary.json', 'r') as file:
        feature_data = json.load(file)
    print(spacer)
    # print("Initial Postman File:", custom_postman)
    print(spacer)

    # ====================================================================================================================
    # Might want this it captures all configuration lines and generates a dictionary with sub configuration.
    with open(sw_config, 'r') as file:
        lines = file.readlines()
        config_dict = {}
        deduped_lines = {}
        for i, line in enumerate(lines):
            if not line.startswith(' '):  # Detect top-level configuration lines
                sub_config_lines = []
                j = i + 1
                while j < len(lines) and lines[j].startswith(' ' * 3):
                    sub_config_lines.append(lines[j].strip())
                    j += 1
                config_dict[line.strip()] = sub_config_lines
                # print(f"Line '{line.strip()}' has sub-configuration: {sub_config_lines}")
    # pprint(config_dict, indent=4)
    # Remove repeated configurations for interfaces.
    for line, sub_config in config_dict.items():
        if interface_context.search(line):
            if sub_config:  # Only deduplicate if there is a sub-configuration
                if any(sub_config == sub_list for sub_list in deduped_lines.values()):
                    for matched_line, deduped_sub_config in deduped_lines.items():
                        if deduped_sub_config == sub_config:
                            # print(f"deduped line: {matched_line}, deduped sub config: {deduped_sub_config} and sub config: {sub_config}")
                            # pprint(
                            #     f"deduped line: {matched_line}, deduped sub config: {deduped_sub_config} and sub config: {sub_config}")
                            formatted_matched_line = matched_line + "," + line.strip("interface")
                            deduped_lines[formatted_matched_line] = deduped_sub_config
                            del deduped_lines[matched_line]
                            break
                else:
                    deduped_lines[line] = sub_config
            else:
                deduped_lines[line] = sub_config
        else:
            deduped_lines[line] = sub_config
    # pprint(deduped_lines, indent=4)
    # =====================================================================================================================
    #
    api_call_counter = {}
    folder_description = {}

    for line, sub_config in deduped_lines.items():
        # Print the current line and its sub-configuration
        if line not in line_matched:
            # Detect if the line has a Postman API call
            detector = detect_postman(line, feature_data)
            if detector:
                print(spacer)
                print(f'Postman call available, matched line: {line}, {sub_config}')
                parser = detector[1]
                api_name = detector[2]
                postman_api_call_name = detector[3]
                # Check if the API folder already exists in the custom Postman collection
                key_list = find_key(custom_postman, api_name)
                if api_name in key_list:
                    # Initialize the counter for the API name if not already done
                    if api_name not in api_call_counter:
                        api_call_counter[api_name] = 2
                    else:
                        api_call_counter[api_name] += 1
                    folder_description[api_name] += f"{line}\n "
                    # Append the updated API call to the existing folder
                    for value in custom_postman["item"]:
                        if api_name == value['name']:
                            for item in value['item']:
                                if "body" in item['request']:
                                    # Save original API call, before attempting to update it
                                    original_call = copy.deepcopy(item)
                                    try_update_api = customize_api_call(parser, item, line, api_name)
                                    if sub_config != []:
                                        for sub_line in sub_config:
                                            detector = detect_postman(sub_line, feature_data)
                                            if detector:
                                                parser = detector[1]
                                                sub_line_api_name = detector[2]
                                                print(f"Sub line: {sub_line}")
                                                try_update_api = customize_api_call(parser, try_update_api, sub_line,
                                                                                    sub_line_api_name)
                                                # updated_description_api_call = update_api_description(try_update_api, sub_line)
                                                folder_description[api_name] += f"{sub_line}\n "
                                    # If original API call is different, that means a value was updated
                                    # There is no need to replace the old value with the new value.
                                    # Because we are referencing the same object in memory. Python will update the value.
                                    # we break the loop to prevent the same API call from being added multiple times.
                                    if try_update_api['request']['body']['raw'] != original_call['request']['body']['raw'] and api_name in single_call:
                                            print(f'Original API call, updated with new values')
                                            line_matched.append(line)
                                            print(spacer)
                                            break
                                    # If the original API call is the same as the updated API call, create a new API call
                                    else:
                                        print(f"Folder Created for call already, adding call to folder")
                                        # Grabs the collection folder and the API call from the postman database
                                        detector = detect_postman(line, feature_data)
                                        parser = detector[1]
                                        api_name = detector[2]
                                        postman_api_call_name = detector[3]
                                        new_collection_folder = postman_folder_creation(profiles, api_name,
                                                                                        postman_api_call_name)
                                        print("Configuring custom API call")
                                        updated_api_call = customize_api_call(parser, new_collection_folder[1], line,
                                                                              api_name)
                                        updated_api_call['name'] = updated_api_call[
                                                                       'name'] + f' {api_call_counter[api_name]}'
                                        if sub_config != []:
                                            for sub_line in sub_config:
                                                detector = detect_postman(sub_line, feature_data)
                                                if detector:
                                                    parser = detector[1]
                                                    sub_line_api_name = detector[2]
                                                    print(f"Sub line: {sub_line}")
                                                    updated_api_call = customize_api_call(parser, updated_api_call,
                                                                                          sub_line, sub_line_api_name)
                                                    # updated_api_call = update_api_description(
                                                    #     updated_api_call, sub_line)
                                        value['item'].append(updated_api_call)
                                        print(f'Updated Postman file 2')
                                        line_matched.append(line)
                                        print(spacer)
                                        break
                else:
                    print(f"Creating API folder")
                    # Create a new API folder and configure the custom API call
                    new_collection_folder = postman_folder_creation(profiles, api_name, postman_api_call_name)
                    if new_collection_folder is not None:

                        print(f"Folder Created for {api_name}:\n{new_collection_folder[0]}")
                        print("Configuring custom API call")
                        updated_api_call = customize_api_call(parser, new_collection_folder[1], line, api_name)
                        folder_description[api_name] = f"\n{line}\n "
                        # print(f"Returned API call: {updated_api_call}")
                        if sub_config != []:
                            print((f"Sub config found : {sub_config}"))
                            for sub_line in sub_config:
                                detector = detect_postman(sub_line, feature_data)
                                if detector:
                                    parser = detector[1]
                                    sub_line_api_name = detector[2]
                                    print(f"Sub line: {sub_line}")
                                    updated_api_call = customize_api_call(parser, updated_api_call, sub_line, sub_line_api_name)
                                    folder_description[api_name] += f"{sub_line}\n "
                                    # updated_api_call = update_api_description(
                                    #     updated_api_call, sub_line)

                            # Initialize the counter for the API name
                        api_call_counter[api_name] = 1
                        updated_api_call['name'] = updated_api_call['name'] + f' {api_call_counter[api_name]}'
                        new_collection_folder[0]['item'].append(updated_api_call)
                        custom_postman['item'].append(new_collection_folder[0])

    for item in custom_postman['item']:
        if item['name'] in folder_description:
            item['description'] += folder_description[item['name']]
        # print(item['description'])


    # pprint(custom_postman)
    with open(custom_postman_collection, 'w') as file:
        json.dump(custom_postman, file)


print(app.registered_commands)







if __name__ == "__main__":
    app()
