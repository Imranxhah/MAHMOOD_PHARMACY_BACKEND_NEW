try:
    with open('temp_reqs.txt', 'r', encoding='utf-16') as f:
        print(f.read())
except Exception as e:
    try:
         with open('temp_reqs.txt', 'r', encoding='utf-8') as f:
            print(f.read())
    except Exception as e2:
        print(f"Error: {e}, {e2}")
