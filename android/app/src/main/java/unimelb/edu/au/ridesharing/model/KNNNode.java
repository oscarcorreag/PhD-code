package unimelb.edu.au.ridesharing.model;

public class KNNNode {
    private long nodeId;
    private double longitude;
    private double latitude;
    private double distance;

    public long getNodeId() {
        return nodeId;
    }

    public void setNodeId(long nodeId) {
        this.nodeId = nodeId;
    }

    public double getLongitude() {
        return longitude;
    }

    public void setLongitude(double longitude) {
        this.longitude = longitude;
    }

    public double getLatitude() {
        return latitude;
    }

    public void setLatitude(double latitude) {
        this.latitude = latitude;
    }

    public double getDistance() {
        return distance;
    }

    public void setDistance(double distance) {
        this.distance = distance;
    }
}
