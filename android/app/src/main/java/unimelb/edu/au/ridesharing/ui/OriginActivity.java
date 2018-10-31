package unimelb.edu.au.ridesharing.ui;

import android.support.v4.app.FragmentActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.ProgressBar;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.BitmapDescriptor;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.MarkerOptions;

import java.util.List;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.SessionNode;
import unimelb.edu.au.ridesharing.model.SessionUser;
import unimelb.edu.au.ridesharing.rest.SessionController;
import unimelb.edu.au.ridesharing.rest.SessionNodeController;
import unimelb.edu.au.ridesharing.rest.SessionUserController;

public class OriginActivity extends FragmentActivity implements
        OnMapReadyCallback,
        SessionUserController.SessionUserControllerListener,
        SessionNodeController.PoisListener,
        SessionController.ComputePlanSessionControllerListener {

    private static final String TAG = OriginActivity.class.getName();

    SessionUser mSessionUser;
    String mActivity;
    private GoogleMap mMap;
    ProgressBar mProgressBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_origin);

        mSessionUser = getIntent().getParcelableExtra("sessionUser");
        mActivity = getIntent().getStringExtra("activity");

        mProgressBar = findViewById(R.id.origin_progressBar);

        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
        assert mapFragment != null;

        mProgressBar.setVisibility(View.VISIBLE);

        mapFragment.getMapAsync(this);
    }


    /**
     * Manipulates the map once available.
     * This callback is triggered when the map is ready to be used.
     * This is where we can add markers or lines, add listeners or move the camera. In this case,
     * we just add a marker near Sydney, Australia.
     * If Google Play services is not installed on the device, the user will be prompted to install
     * it inside the SupportMapFragment. This method will only be triggered once the user has
     * installed Google Play services and returned to the app.
     */
    @Override
    public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;

        SessionUserController sessionUserController = new SessionUserController();
        sessionUserController.setSessionUserListener(this);
        sessionUserController.getUser(mSessionUser.getUser().getUsername(), mSessionUser.getSessionId(), mSessionUser.getUserId());
    }

    @Override
    public void processSessionUser(SessionUser sessionUser, ResponseStatus responseStatus) {
        if (responseStatus.isSuccessful()) {
            // DO NOT OVERRIDE Session and User objects.
            mSessionUser.update(sessionUser);
            // Add a marker in origin and move the camera.
            mMap.addMarker(new MarkerOptions().position(mSessionUser.getLatLngOrigin()).title(mSessionUser.getUser().getUsername()));
//            mMap.moveCamera(CameraUpdateFactory.newLatLngBounds(mSessionUser.getSession().getBounds(), 0));
            mMap.moveCamera(CameraUpdateFactory.newLatLngZoom(mSessionUser.getLatLngOrigin(), 15));

            SessionNodeController sessionNodeController = new SessionNodeController();
            sessionNodeController.setPoisListener(this);
            sessionNodeController.getPois(mSessionUser.getUser().getUsername(), mSessionUser.getSessionId(), mActivity);
        } else{
            mProgressBar.setVisibility(View.GONE);
            showMsgFragment("Error", responseStatus.getDetail());
        }
    }

    @Override
    public void processPois(List<SessionNode> pois, ResponseStatus responseStatus) {

        mProgressBar.setVisibility(View.GONE);

        if (responseStatus.isSuccessful()) {
            BitmapDescriptor bitmapDescriptor = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_AZURE);
            for (SessionNode poi : pois) {
                mMap.addMarker(new MarkerOptions()
                        .position(poi.getLatLng())
                        .icon(bitmapDescriptor));
            }
        } else {
            showMsgFragment("Error", responseStatus.getDetail());
        }
    }

    private void showMsgFragment(String title, String message) {
        MsgDialogFragment msgDialogFragment = new MsgDialogFragment();
        Bundle args = new Bundle();

        args.putCharSequence("title", title);
        args.putCharSequence("message", message);
        msgDialogFragment.setArguments(args);
        msgDialogFragment.show(getSupportFragmentManager(), "MsgDialogFragment");
    }

    public void computePlan(View v) {
        SessionController sessionController = new SessionController();
        sessionController.setComputePlanSessionListener(this);
        sessionController.computePlan(mSessionUser.getUser().getUsername(), mSessionUser.getSessionId(), mSessionUser.getUserId(), mActivity);
    }

    @Override
    public void processResponseComputePlan(ResponseStatus responseStatus) {
        if (responseStatus.isSuccessful()) {
            showMsgFragment("Info", responseStatus.getDetail());
        } else {
            showMsgFragment("Error", responseStatus.getDetail());
        }
    }
}
