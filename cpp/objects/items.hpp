#include "../lib/utils.hpp"
#include "../lib/area.hpp"
#include <memory>
#include <map>
#include "BearLibTerminal.h"

#pragma once
namespace items
{
    void load_items();
    enum class WBC
    {
        Weapon,
        Armor,
        RangedWeapon,
        Missle,
        Light,
        Food
    };

    struct Item
    {
        std::string name;
        std::vector<std::string> categories;
        char c;
        color_t color;
        WBC broad_category;
        int weight;
        int probability;

        // Weapon
        int handedness;
        int attack;

        // Armor
        int defence;

        // Ranged Weapon
        int range;
        int load_speed;

        // Missle
        int hit;
        int accuracy;

        // Light
        int radius;
        int lasts;

        // Food
        int nutrition;
    };

    extern std::map<std::string, Item> ITEMS;

    enum class ItemValType
    {
        String, StringVector, Integer, Empty
    };

    struct ItemVal
    {
        ItemValType type;
        std::string str;
        std::vector<std::string> strv;
        int i = 0;
    };

    typedef std::map<std::string,  ItemVal> ItemMap;
}
