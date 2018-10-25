package unimelb.edu.au.ridesharing.rest;

import android.annotation.SuppressLint;

import java.util.HashMap;
import java.util.Map;

public enum StatusCode {
    OK(200, "ok"),
    CREATED(201, "created"),
    INTERNAL_SERVER_ERROR(500, "internal_server_error");

    private final int mCode;
    private final String mDetailCode;

    @SuppressLint("UseSparseArrays")
    private static Map<Integer, StatusCode> map = new HashMap<>();

    static {
        for (StatusCode statusCode : StatusCode.values()) {
            map.put(statusCode.mCode, statusCode);
        }
    }

    StatusCode(int code, String detailCode) {
        this.mCode = code;
        this.mDetailCode = detailCode;
    }

    public int getCode() {
        return mCode;
    }

    public String getDetailCode() {
        return mDetailCode;
    }

    public static StatusCode fromValue(int code) {
        return map.get(code);
    }
}
