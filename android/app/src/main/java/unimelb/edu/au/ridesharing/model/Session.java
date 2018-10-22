package unimelb.edu.au.ridesharing.model;

import com.google.gson.annotations.SerializedName;

import java.util.Date;

public class Session {
    @SerializedName("start_time")
    private Date startTime;
    @SerializedName("end_time")
    private Date endTime;
    private String city;
    private boolean current;
    private int creator;
    @SerializedName("real_users")
    private int realUsers;
    @SerializedName("simulated_users")
    private int simulatedUsers;

    public Date getStartTime() {
        return startTime;
    }

    public void setStartTime(Date startTime) {
        this.startTime = startTime;
    }

    public Date getEndTime() {
        return endTime;
    }

    public void setEndTime(Date endTime) {
        this.endTime = endTime;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public boolean isCurrent() {
        return current;
    }

    public void setCurrent(boolean current) {
        this.current = current;
    }

    public int getCreator() {
        return creator;
    }

    public void setCreator(int creator) {
        this.creator = creator;
    }

    public int getRealUsers() {
        return realUsers;
    }

    public void setRealUsers(int realUsers) {
        this.realUsers = realUsers;
    }

    public int getSimulatedUsers() {
        return simulatedUsers;
    }

    public void setSimulatedUsers(int simulatedUsers) {
        this.simulatedUsers = simulatedUsers;
    }
}
