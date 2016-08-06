import pgoapi
import json
import time
from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cleanup', methods=['POST'])
def cleanup():
    api = pgoapi.PGoApi()
    api.set_position(40.7127837, -74.005941, 0.0)
    auth_success = api.login(request.form['type'], request.form['username'], request.form['password'])
    if not auth_success:
        return "Auth failure"
    inventory_items = api.get_inventory()['responses']['GET_INVENTORY']['inventory_delta']['inventory_items']
    pokemons = [ii['inventory_item_data']['pokemon_data'] for ii in inventory_items if 'pokemon_data' in ii['inventory_item_data']]
    pokemon_by_type = {}
    for pokemon in pokemons:
        if 'egg_km_walked_target' in pokemon:
            continue # Egg
        pokemon_by_type.setdefault(pokemon['pokemon_id'], [])
        pokemon_by_type[pokemon['pokemon_id']].append(pokemon)

    for pokemon_type, pokemons in pokemon_by_type.items():
        pokemon_by_type[pokemon_type] = sorted(pokemons, key=lambda i: i["cp"], reverse=True)
    for pokemon_type, pokemons in pokemon_by_type.items():
        assert int(request.form['n']) > 0 # Not removing all pokemons
        for eligible_pokemon in pokemons[int(request.form['n']):]:
            if eligible_pokemon['cp'] > request.form['cp']:
                continue
            print("Releasing %d" % pokemon_type)
            time.sleep(0.5)
            api.release_pokemon(pokemon_id=eligible_pokemon['id'])
    return "Done"

if __name__ == "__main__":
        app.run()
