package unimelb.edu.au.ridesharing.model;

import com.google.android.gms.maps.model.LatLng;
import com.google.gson.annotations.SerializedName;

public class SessionNode {

    private Session mSession;

    @SerializedName("id")
    private int mId;
    @SerializedName("session")
    private int mSessionId;
    @SerializedName("node")
    private long mNode;
    @SerializedName("node_type")
    private char mType;
    @SerializedName("activity")
    private String mActivity;
    @SerializedName("longitude")
    private double mLongitude;
    @SerializedName("latitude")
    private double mLatitude;

    public Session getSession() {
        return mSession;
    }

    public void setmSession(Session session) {
        this.mSession = session;
    }

    public int getId() {
        return mId;
    }

    public void setId(int id) {
        this.mId = id;
    }

    public int getSessionId() {
        return mSessionId;
    }

    public void setSessionId(int sessionId) {
        this.mSessionId = sessionId;
    }

    public long getNode() {
        return mNode;
    }

    public void setNode(long node) {
        this.mNode = node;
    }

    public char getType() {
        return mType;
    }

    public void setType(char type) {
        this.mType = type;
    }

    public String getActivity() {
        return mActivity;
    }

    public void setActivity(String activity) {
        this.mActivity = activity;
    }

    public double getLongitude() {
        return mLongitude;
    }

    public void setLongitude(double longitude) {
        this.mLongitude = longitude;
    }

    public double getLatitude() {
        return mLatitude;
    }

    public void setLatitude(double latitude) {
        this.mLatitude = latitude;
    }

    public LatLng getLatLng() {
        return new LatLng(this.mLatitude, this.mLongitude);
    }
}
