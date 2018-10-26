package unimelb.edu.au.ridesharing.model;

import com.google.gson.annotations.SerializedName;

public class SessionActivity {
    @SerializedName("session")
    private int mSessionId;
    @SerializedName("activity")
    private String mActivity;

    public int getSessionId() {
        return mSessionId;
    }

    public void setSessionId(int sessionId) {
        this.mSessionId = sessionId;
    }

    public String getActivity() {
        return mActivity;
    }

    public void setActivity(String activity) {
        this.mActivity = activity;
    }
}
