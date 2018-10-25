package unimelb.edu.au.ridesharing.model;

import java.util.HashMap;
import java.util.Map;

public enum City {
    MELBOURNE("MEL", "MELBOURNE"),
    MANHATTAN("MHK", "MANHATTAN"),
    QUITO("UIO", "QUITO");

    private final String mIataCode;
    private final String mName;

    private static Map<String, City> map = new HashMap<>();

    static {
        for (City city : City.values()) {
            map.put(city.mIataCode, city);
        }
    }

    City(String iataCode, String name) {
        this.mIataCode = iataCode;
        this.mName = name;
    }

    public String getIataCode() {
        return mIataCode;
    }

    public String getName() {
        return mName;
    }

    public static City fromValue(String iataCode) {
        return map.get(iataCode);
    }
}
