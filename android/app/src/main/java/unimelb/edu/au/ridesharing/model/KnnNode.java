package unimelb.edu.au.ridesharing.model;

public class KnnNode {

    private long node;
    private double longitude;
    private double latitude;
    private double distance;

    public long getNode() {
        return node;
    }

    public void setNode(long node) {
        this.node = node;
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
