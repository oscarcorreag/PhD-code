package unimelb.edu.au.ridesharing.rest;

import android.support.annotation.NonNull;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import unimelb.edu.au.ridesharing.model.KnnNode;

public class KnnNodesController implements Callback<List<KnnNode>> {

    public void get(double longitude, double latitude, int k) {
        Call<List<KnnNode>> call = RsRestService.getInstance().getService().knnNodes(longitude, latitude, k);
        call.enqueue(this);
    }

    @Override
    public void onResponse(@NonNull Call<List<KnnNode>> call, @NonNull Response<List<KnnNode>> response) {
        if (response.isSuccessful()) {
            List<KnnNode> nodes = response.body();
            if (nodes != null) {
                nodes.forEach(node -> System.out.println("node:" + node.getNode()));
            }
        } else {
            System.out.println(response.errorBody());
        }
    }

    @Override
    public void onFailure(@NonNull Call<List<KnnNode>> call, @NonNull Throwable t) {
        t.printStackTrace();
    }
}
