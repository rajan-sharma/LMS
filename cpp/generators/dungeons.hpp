#include "../lib/utils.hpp"
#include "../lib/area.hpp"
#include "../lib/consts.hpp"
#include <memory>
#include <set>

#pragma once
namespace dungeons
{
    enum class StaticMapElement
    {
        Floor,
        Fire,
        Water,
        GeneralObject,
        OpenDoor,
        ClosedDoor,
        Wall,
        UpStairs,
        DownStairs,
        TeleportTrap,
        FreeseTrap,
        TrapDoorTrap
    };

    struct MapElement
    {
        StaticMapElement sme;
        std::vector<std::shared_ptr<items::Item> > i;
        std::vector<std::shared_ptr<monsters::Monster> > m;
    };
    struct Dungeon
    {
        std::vector<monsters::Monster> monsters{};
        bool alerted = false;
        std::set<area::Area> areas{};
        MapElement map[consts::HEIGHT][consts::WIDTH]{};
        std::set<area::Point> remembered{};
        area::Point player_start{-1, -1};
    };

    template <class T>
    Dungeon generate_new(std::unique_ptr<T>);
    template <class T>
    Dungeon generate_bsp(std::unique_ptr<T>);
    template <class T>
    Dungeon generate_walker(std::unique_ptr<T>);
    Dungeon empty_dungeon();
}
