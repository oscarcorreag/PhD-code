package unimelb.edu.au.ridesharing.ui;

import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
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
import com.google.android.gms.maps.model.PolylineOptions;

import java.util.List;
import java.util.Locale;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.Activity;
import unimelb.edu.au.ridesharing.model.SessionNode;
import unimelb.edu.au.ridesharing.model.SessionRouteEdge;
import unimelb.edu.au.ridesharing.model.SessionUser;
import unimelb.edu.au.ridesharing.rest.SessionNodeController;
import unimelb.edu.au.ridesharing.rest.SessionRouteEdgeController;
import unimelb.edu.au.ridesharing.rest.SessionUserController;

public class PlanActivity extends FragmentActivity implements
        OnMapReadyCallback,
        SessionRouteEdgeController.SessionRouteControllerListener,
        SessionUserController.RouteMatesControllerListener,
        SessionNodeController.PoisListener {

    SessionUser mSessionUser;
    GoogleMap mMap;
    ProgressBar mProgressBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_plan);

        mSessionUser = getIntent().getParcelableExtra("sessionUser");

        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
        assert mapFragment != null;

        mProgressBar = findViewById(R.id.plan_progressBar);
        mProgressBar.setVisibility(View.VISIBLE);
        mapFragment.getMapAsync(this);

        FloatingActionButton fab = findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(view, "Here's a Snackbar", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
            }
        });
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

        SessionNodeController sessionNodeController = new SessionNodeController();
        sessionNodeController.setPoisListener(this);
        sessionNodeController.getPois(mSessionUser.getUser().getUsername(), mSessionUser.getSessionId(), mSessionUser.getActivity());
    }

    @Override
    public void processSessionRoute(List<SessionRouteEdge> route, ResponseStatus responseStatus) {

        mProgressBar.setVisibility(View.GONE);

        if (responseStatus.isSuccessful()) {
            for (SessionRouteEdge edge : route) {
                mMap.addPolyline(new PolylineOptions().add(edge.getLatLngNodeI(), edge.getLatLngNodeJ()));
            }
            mMap.moveCamera(CameraUpdateFactory.newLatLngZoom(mSessionUser.getLatLngOrigin(), 13));
        } else {
            showMsgFragment(responseStatus.getDetail());
        }
    }

    private void showMsgFragment(String message) {
        MsgDialogFragment msgDialogFragment = new MsgDialogFragment();
        Bundle args = new Bundle();

        args.putCharSequence("title", "Error");
        args.putCharSequence("message", message);
        msgDialogFragment.setArguments(args);
        msgDialogFragment.show(getSupportFragmentManager(), "MsgDialogFragment");
    }

    @Override
    public void processRouteMates(List<SessionUser> mates, ResponseStatus responseStatus) {
        if (responseStatus.isSuccessful()) {

            SessionRouteEdgeController sessionRouteEdgeController = new SessionRouteEdgeController();
            sessionRouteEdgeController.setSessionRouteListener(this);
            sessionRouteEdgeController.getSessionRoute(mSessionUser.getUser().getUsername(), mSessionUser.getId());

            BitmapDescriptor bdSimulatedUsers = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_CYAN);
            for (SessionUser mate : mates) {
                if (mate.isReadyToTravel()) {  // This corresponds to real users
                    mMap.addMarker(new MarkerOptions()
                            .position(mate.getLatLngOrigin())
                            .title(mSessionUser.getUser().getUsername()));
                } else {
                    mMap.addMarker(new MarkerOptions()
                            .position(mate.getLatLngOrigin())
                            .title(String.format(Locale.getDefault(), "User %d", mate.getId()))
                            .icon(bdSimulatedUsers));
                }
            }
        } else {
            mProgressBar.setVisibility(View.GONE);
            showMsgFragment(responseStatus.getDetail());
        }
    }

    @Override
    public void processPois(List<SessionNode> pois, ResponseStatus responseStatus) {

        if (responseStatus.isSuccessful()) {
            SessionUserController sessionUserController = new SessionUserController();
            sessionUserController.setRouteMatesListener(this);
            sessionUserController.getRouteMates(mSessionUser.getUser().getUsername(), mSessionUser.getSessionId(), mSessionUser.getId());

            int resId = Activity.fromValue(mSessionUser.getActivity()).getResourceId();
            BitmapDescriptor bdPois = BitmapDescriptorFactory.fromResource(resId);
            for (SessionNode poi : pois) {
                mMap.addMarker(new MarkerOptions()
                        .position(poi.getLatLng())
                        .icon(bdPois));
            }

        } else {
            mProgressBar.setVisibility(View.GONE);
            showMsgFragment(responseStatus.getDetail());
        }
    }
}
