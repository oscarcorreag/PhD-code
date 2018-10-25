package unimelb.edu.au.ridesharing.model;

import java.util.HashMap;
import java.util.Map;

import unimelb.edu.au.ridesharing.R;

public enum Activity {
    POST_OFFICE("amenity:post_office", R.mipmap.ic_post_office, "POST OFFICE"),
    SHOP_MALL("shop:mall", R.mipmap.ic_shop_mall, "SHOP MALL"),
    RESTAURANT("amenity:restaurant", R.mipmap.ic_restaurant, "RESTAURANT"),
    SUPERMARKET("shop:supermarket", R.mipmap.ic_supermarket, "SUPERMARKET"),
    CONVENIENCE("shop:convenience", R.mipmap.ic_convenience, "CONVENIENCE STORE"),
    SWIMMING_POOL("leisure:swimming_pool", R.mipmap.ic_swimming_pool, "SWIMMING POOL"),
    BAR("amenity:bar", R.mipmap.ic_bar, "BAR"),
    FAST_FOOD("amenity:fast_food", R.mipmap.ic_fast_food, "FAST FOOD"),
    CAFE("amenity:cafe", R.mipmap.ic_cafe, "CAFE"),
    FITNESS_CENTRE("leisure:fitness_centre", R.mipmap.ic_fitness_centre, "FITNESS CENTRE"),
    PUB("amenity:pub", R.mipmap.ic_bar, "PUB");

    private final String mOsmCode;
    private final int mResourceId;
    private final String mName;

    private static Map<String, Activity> map = new HashMap<>();

    static {
        for (Activity activity : Activity.values()) {
            map.put(activity.mOsmCode, activity);
        }
    }

    Activity(String osmCode, int resourceId, String name) {
        this.mOsmCode = osmCode;
        this.mResourceId = resourceId;
        this.mName = name;
    }

    public String getOsmCode() {
        return mOsmCode;
    }

    public int getResourceId() {
        return mResourceId;
    }

    public String getName() {
        return mName;
    }

    public static Activity fromValue(String osmCode) {
        return map.get(osmCode);
    }
}
