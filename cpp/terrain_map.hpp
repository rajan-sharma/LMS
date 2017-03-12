#include "lib/utils.hpp"
#include "generators/dungeons.hpp"
#include "lib/area.hpp"
#include <memory>
#include <vector>
#include <set>

#pragma once
namespace terrain_map
{
    class TerrainMap
    {
    private:
        std::vector<dungeons::Dungeon> dungeons;
        uint width;
        uint height;

    public:
        bool restore_dungeon(int n);
        dungeons::Dungeon dungeon;
        uint level;
        std::set<area::Point> fov;

        TerrainMap() = default;
        TerrainMap(uint w, uint h);

        // Mutating Functions
        void calculate_fov(area::Point p);
        void generate_dungeon_map();
        bool generate_new_map();
        void put_cell(area::Point p, dungeons::MapElement el);

        // Constant Functions
        template <class T>
        void draw_map(std::shared_ptr<T> gs, uint frame) const;

        dungeons::MapElement& operator[](area::Point p) const;
        bool contains(area::Point x, bool bordered) const;
        area::Area area_at(area::Point p) const;
        bool walkable(area::Point p) const;
        std::vector<area::Area> generate_areas() const;
        bool operator>(area::Point p) const;
        bool operator>=(area::Point p) const;
    };
}
