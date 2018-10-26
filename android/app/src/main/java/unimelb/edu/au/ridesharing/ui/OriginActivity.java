package unimelb.edu.au.ridesharing.ui;

import android.support.v4.app.FragmentActivity;
import android.os.Bundle;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.SessionUser;
import unimelb.edu.au.ridesharing.rest.SessionUserController;

public class OriginActivity extends FragmentActivity implements
        OnMapReadyCallback,
        SessionUserController.SessionUserControllerListener {

    SessionUser mSessionUser;
    private GoogleMap mMap;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_origin);

        mSessionUser = getIntent().getParcelableExtra("sessionUser");

        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
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
        sessionUserController.getUser(mSessionUser.getSessionId(), mSessionUser.getUserId());
    }

    @Override
    public void processSessionUser(SessionUser sessionUser, ResponseStatus responseStatus) {
        if (responseStatus.isSuccessful()) {
            mSessionUser = sessionUser;

            // Add a marker in origin and move the camera.
            LatLng origin = new LatLng(mSessionUser.getLatitude(), mSessionUser.getLongitude());
            mMap.addMarker(new MarkerOptions().position(origin).title("Marker in Sydney"));
            mMap.moveCamera(CameraUpdateFactory.newLatLng(origin));
        }
    }
}
