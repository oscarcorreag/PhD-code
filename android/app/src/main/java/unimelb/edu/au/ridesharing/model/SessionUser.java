package unimelb.edu.au.ridesharing.model;

import android.os.Parcel;
import android.os.Parcelable;

import com.google.android.gms.maps.model.LatLng;
import com.google.gson.annotations.SerializedName;

import java.util.Date;

public class SessionUser implements Parcelable {

    private Session mSession;

    private User mUser;

    @SerializedName("id")
    private int mId;
    @SerializedName("session")
    private int mSessionId;
    @SerializedName("user")
    private int mUserId;
    @SerializedName("join_time")
    private Date mJoinTime;
    @SerializedName("origin")
    private long mOrigin;
    @SerializedName("destination")
    private long mDestination;
    @SerializedName("activity")
    private String mActivity;
    @SerializedName("vehicle")
    private int mVehicle;
    @SerializedName("ready_to_travel")
    private boolean mReadyToTravel;
    @SerializedName("longitude")
    private double mLongitude;
    @SerializedName("latitude")
    private double mLatitude;

    public SessionUser(int sessionId, int userId) {
        this.mSessionId = sessionId;
        this.mUserId = userId;
    }

    protected SessionUser(Parcel in) {
        mSession = in.readParcelable(Session.class.getClassLoader());
        mUser = in.readParcelable(User.class.getClassLoader());
        mId = in.readInt();
        mSessionId = in.readInt();
        mUserId = in.readInt();
        mOrigin = in.readLong();
        mDestination = in.readLong();
        mActivity = in.readString();
        mVehicle = in.readInt();
        mReadyToTravel = in.readByte() != 0;
        mLongitude = in.readDouble();
        mLatitude = in.readDouble();
    }

    public static final Creator<SessionUser> CREATOR = new Creator<SessionUser>() {
        @Override
        public SessionUser createFromParcel(Parcel in) {
            return new SessionUser(in);
        }

        @Override
        public SessionUser[] newArray(int size) {
            return new SessionUser[size];
        }
    };

    public Session getSession() {
        return mSession;
    }

    public void setSession(Session session) {
        this.mSession = session;
    }

    public User getUser() {
        return mUser;
    }

    public void setUser(User user) {
        this.mUser = user;
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

    public int getUserId() {
        return mUserId;
    }

    public void setUserId(int userId) {
        this.mUserId = userId;
    }

    public Date getJoinTime() {
        return mJoinTime;
    }

    public void setJoinTime(Date joinTime) {
        this.mJoinTime = joinTime;
    }

    public long getOrigin() {
        return mOrigin;
    }

    public void setOrigin(long origin) {
        this.mOrigin = origin;
    }

    public long getDestination() {
        return mDestination;
    }

    public void setDestination(long destination) {
        this.mDestination = destination;
    }

    public String getActivity() {
        return mActivity;
    }

    public void setActivity(String activity) {
        this.mActivity = activity;
    }

    public int getVehicle() {
        return mVehicle;
    }

    public void setVehicle(int vehicle) {
        this.mVehicle = vehicle;
    }

    public boolean isReadyToTravel() {
        return mReadyToTravel;
    }

    public void setReadyToTravel(boolean readyToTravel) {
        this.mReadyToTravel = readyToTravel;
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

    public LatLng getLatLngOrigin() {
        return new LatLng(this.mLatitude, this.mLongitude);
    }

    @Override
    public int describeContents() {
        return 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeParcelable(mSession, flags);
        dest.writeParcelable(mUser, flags);
        dest.writeInt(mId);
        dest.writeInt(mSessionId);
        dest.writeInt(mUserId);
        dest.writeLong(mOrigin);
        dest.writeLong(mDestination);
        dest.writeString(mActivity);
        dest.writeInt(mVehicle);
        dest.writeByte((byte) (mReadyToTravel ? 1 : 0));
        dest.writeDouble(mLongitude);
        dest.writeDouble(mLatitude);
    }

    public void update(SessionUser other) {
        this.mId = other.mId;
        this.mOrigin = other.mOrigin;
        this.mDestination = other.mDestination;
        this.mActivity = other.mActivity;
        this.mVehicle = other.mVehicle;
        this.mReadyToTravel = other.mReadyToTravel;
        this.mLongitude = other.mLongitude;
        this.mLatitude = other.mLatitude;
    }
}
