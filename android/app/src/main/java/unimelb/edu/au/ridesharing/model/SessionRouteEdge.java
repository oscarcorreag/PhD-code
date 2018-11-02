package unimelb.edu.au.ridesharing.model;

import com.google.android.gms.maps.model.LatLng;
import com.google.gson.annotations.SerializedName;

public class SessionRouteEdge {

    @SerializedName("id")
    private int mId;
    @SerializedName("node_i")
    private long mNodeI;
    @SerializedName("node_i_longitude")
    private double mNodeILongitude;
    @SerializedName("node_i_latitude")
    private double mNodeILatitude;
    @SerializedName("node_j")
    private long mNodeJ;
    @SerializedName("node_j_longitude")
    private double mNodeJLongitude;
    @SerializedName("node_j_latitude")
    private double mNodeJLatitude;
    @SerializedName("vehicle_id")
    private int mVehicleId;

    public int getId() {
        return mId;
    }

    public void setId(int id) {
        this.mId = id;
    }

    public long getNodeI() {
        return mNodeI;
    }

    public void setNodeI(long nodeI) {
        this.mNodeI = nodeI;
    }

    public double getNodeILongitude() {
        return mNodeILongitude;
    }

    public void setNodeILongitude(double nodeILongitude) {
        this.mNodeILongitude = nodeILongitude;
    }

    public double getNodeILatitude() {
        return mNodeILatitude;
    }

    public void setNodeILatitude(double nodeILatitude) {
        this.mNodeILatitude = nodeILatitude;
    }

    public long getNodeJ() {
        return mNodeJ;
    }

    public void setNodeJ(long nodeJ) {
        this.mNodeJ = nodeJ;
    }

    public double getNodeJLongitude() {
        return mNodeJLongitude;
    }

    public void setNodeJLongitude(double nodeJLongitude) {
        this.mNodeJLongitude = nodeJLongitude;
    }

    public double getNodeJLatitude() {
        return mNodeJLatitude;
    }

    public void setNodeJLatitude(double nodeJLatitude) {
        this.mNodeJLatitude = nodeJLatitude;
    }

    public int getVehicleId() {
        return mVehicleId;
    }

    public void setVehicleId(int vehicleId) {
        this.mVehicleId = vehicleId;
    }

    public LatLng getLatLngNodeI() {
        return new LatLng(this.mNodeILatitude, this.mNodeILongitude);
    }

    public LatLng getLatLngNodeJ() {
        return new LatLng(this.mNodeJLatitude, this.mNodeJLongitude);
    }
}
