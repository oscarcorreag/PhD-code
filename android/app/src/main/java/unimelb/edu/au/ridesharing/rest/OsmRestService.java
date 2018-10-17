package unimelb.edu.au.ridesharing.rest;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Query;
import unimelb.edu.au.ridesharing.model.KNNNode;

public interface OsmRestService {

    @GET("/knnnodes")
    Call<List<KNNNode>> knnNodes(@Query("longitude") double longitude, @Query("latitude") double latitude, @Query("k") int k);
}
