package unimelb.edu.au.ridesharing.rest;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.IOException;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;
import unimelb.edu.au.ridesharing.model.KNNNode;

public class OsmRestController implements Callback<List<KNNNode>> {

//    static final String API_URL = "http://4000L-122353-W:8000/";
    static final String API_URL = "http://10.13.196.38:8000/";

    public void start() {
        Gson gson = new GsonBuilder()
                .setLenient()
                .create();
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(API_URL)
                .addConverterFactory(GsonConverterFactory.create(gson))
                .build();
        OsmRestService service = retrofit.create(OsmRestService.class);
        Call<List<KNNNode>> call = service.knnNodes(144.982060, -37.768032, 5);
        call.enqueue(this);
    }

    @Override
    public void onResponse(Call<List<KNNNode>> call, Response<List<KNNNode>> response) {
        if (response.isSuccessful()) {
            List<KNNNode> nodes = response.body();
            if (nodes != null) {
                nodes.forEach(node -> System.out.println(node.getNodeId()));
            }
        } else {
            System.out.println(response.errorBody());
        }
    }

    @Override
    public void onFailure(Call<List<KNNNode>> call, Throwable t) {
        t.printStackTrace();
    }
}
