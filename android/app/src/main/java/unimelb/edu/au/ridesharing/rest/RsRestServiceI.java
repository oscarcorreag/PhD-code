package unimelb.edu.au.ridesharing.rest;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.POST;
import retrofit2.http.Query;
import unimelb.edu.au.ridesharing.model.KnnNode;
import unimelb.edu.au.ridesharing.model.Session;
import unimelb.edu.au.ridesharing.model.User;

public interface RsRestServiceI {

    @GET("/rs/knnnodes")
    Call<List<KnnNode>> knnNodes(@Query("longitude") double longitude, @Query("latitude") double latitude, @Query("k") int k);

    @GET("/rs/users")
    Call<List<User>> getUsers();

    @GET("/rs/sessions")
    Call<List<Session>> getSessions();

    @POST("/rs/sessions")
    void postSession(@Body Session session);
}
