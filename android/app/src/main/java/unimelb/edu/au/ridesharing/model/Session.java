package unimelb.edu.au.ridesharing.model;

import android.os.Parcel;
import android.os.Parcelable;

import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.LatLngBounds;
import com.google.gson.annotations.SerializedName;

import java.util.Date;

public class Session implements Parcelable {
    @SerializedName("id")
    private int mId;
    @SerializedName("start_time")
    private Date mStartTime;
    @SerializedName("end_time")
    private Date mEndTime;
    @SerializedName("city")
    private String mCity;
    @SerializedName("active")
    private boolean mActive;
    @SerializedName("creator")
    private int mCreator;
    @SerializedName("real_users")
    private int mRealUsers;
    @SerializedName("simulated_users")
    private int mSimulatedUsers;
    @SerializedName("min_lon")
    private double mMinLon;
    @SerializedName("min_lat")
    private double mMinLat;
    @SerializedName("max_lon")
    private double mMaxLon;
    @SerializedName("max_lat")
    private double mMaxLat;

    public Session(String city, int creator, int realUsers, int simulatedUsers) {
        mCity = city;
        mCreator = creator;
        mRealUsers = realUsers;
        mSimulatedUsers = simulatedUsers;
    }

    protected Session(Parcel in) {
        mId = in.readInt();
        mCity = in.readString();
        mActive = in.readByte() != 0;
        mCreator = in.readInt();
        mRealUsers = in.readInt();
        mSimulatedUsers = in.readInt();
        mMinLon = in.readDouble();
        mMinLat = in.readDouble();
        mMaxLon = in.readDouble();
        mMaxLat = in.readDouble();
    }

    public static final Creator<Session> CREATOR = new Creator<Session>() {
        @Override
        public Session createFromParcel(Parcel in) {
            return new Session(in);
        }

        @Override
        public Session[] newArray(int size) {
            return new Session[size];
        }
    };

    public int getId() {
        return mId;
    }

    public void setId(int id) {
        this.mId = id;
    }

    public Date getStartTime() {
        return mStartTime;
    }

    public void setStartTime(Date startTime) {
        this.mStartTime = startTime;
    }

    public Date getEndTime() {
        return mEndTime;
    }

    public void setEndTime(Date endTime) {
        this.mEndTime = endTime;
    }

    public String getCity() {
        return mCity;
    }

    public void setCity(String city) {
        this.mCity = city;
    }

    public boolean isActive() {
        return mActive;
    }

    public void setActive(boolean active) {
        this.mActive = active;
    }

    public int getCreator() {
        return mCreator;
    }

    public void setCreator(int creator) {
        this.mCreator = creator;
    }

    public int getRealUsers() {
        return mRealUsers;
    }

    public void setRealUsers(int realUsers) {
        this.mRealUsers = realUsers;
    }

    public int getSimulatedUsers() {
        return mSimulatedUsers;
    }

    public void setSimulatedUsers(int simulatedUsers) {
        this.mSimulatedUsers = simulatedUsers;
    }

    public double getMinLon() {
        return mMinLon;
    }

    public void setMinLon(double minLon) {
        this.mMinLon = minLon;
    }

    public double getMinLat() {
        return mMinLat;
    }

    public void setMinLat(double minLat) {
        this.mMinLat = minLat;
    }

    public double getMaxLon() {
        return mMaxLon;
    }

    public void setMaxLon(double maxLon) {
        this.mMaxLon = maxLon;
    }

    public double getMaxLat() {
        return mMaxLat;
    }

    public void setMaxLat(double maxLat) {
        this.mMaxLat = maxLat;
    }

    public LatLngBounds getBounds() {
        LatLng sw = new LatLng(this.mMinLat, this.mMinLon);
        LatLng ne = new LatLng(this.mMaxLat, this.mMaxLon);
        return new LatLngBounds(sw, ne);
    }

    @Override
    public int describeContents() {
        return 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeInt(mId);
        dest.writeString(mCity);
        dest.writeByte((byte) (mActive ? 1 : 0));
        dest.writeInt(mCreator);
        dest.writeInt(mRealUsers);
        dest.writeInt(mSimulatedUsers);
        dest.writeDouble(mMinLon);
        dest.writeDouble(mMinLat);
        dest.writeDouble(mMaxLon);
        dest.writeDouble(mMaxLat);
    }
}
